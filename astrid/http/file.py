#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mimetypes
import os.path
import stat

from datetime import datetime
from datetime import timedelta

from astrid.core.datetime import parse_http_datetime
from astrid.http.response import HTTPResponse
from astrid.http.cachepolicy import HTTPCachePolicy
from astrid.http.response import forbidden
from astrid.http.response import not_found

HTTP_HEADER_ACCEPT_RANGE_NONE = ('Accept-Ranges', 'none')



def stream_file_handler(environ, start_response, filename, age=None, skip_body=False, version=None, options=None):

    abspath = os.path.abspath(os.path.join(options['STATIC_FOLDER'], filename))
    if not abspath.startswith(options['STATIC_FOLDER']):
        return forbidden()
    if not os.path.exists(abspath):
        return not_found()
    if not os.path.isfile(abspath):
        return forbidden()

    mime_type, encoding = mimetypes.guess_type(abspath)
    response = HTTPResponse(mime_type or 'plain/text', encoding)

    last_modified_stamp = os.stat(abspath)[stat.ST_MTIME]

    etag = '\"' + hex(last_modified_stamp)[2:] + '\"'
    none_match = environ.get('HTTP_IF_NONE_MATCH', None)
    if none_match and etag in none_match:
        response.status_code = 304
        response.skip_body = True
        return response

    last_modified = datetime.utcfromtimestamp(last_modified_stamp)
    modified_since = environ.get('HTTP_IF_MODIFIED_SINCE', None)
    if modified_since:
        modified_since = parse_http_datetime(modified_since)
        if modified_since >= last_modified:
            response.status_code = 304
            response.skip_body = True
            return response

    response.cache_policy = cache_policy = HTTPCachePolicy('public')
    cache_policy.etag(etag)
    cache_policy.last_modified(last_modified)

    if age:
        cache_policy.max_age(age)
        cache_policy.expires(datetime.utcnow() + age)
    if not skip_body:
        response.headers.append(HTTP_HEADER_ACCEPT_RANGE_NONE)
        file = open(abspath, 'rb')
        try:
            response.write_bytes(file.read())
        finally:
            file.close()
    else:
        response.skip_body = True
    return response