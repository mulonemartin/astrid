#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

from astrid.http.response import HTTPResponse, HTTPError, http_error, HTTPRedirect, redirect, HTTPJSONResponse
from astrid.http.request import HTTPRequest
from astrid.http.file import stream_file_handler
from astrid.app.options import bootstrap_defaults
from astrid.web.expose import expose


REGEX_STATIC = re.compile('^/static/(?P<v>_\d+\.\d+\.\d+/)?(?P<f>.*?)$')


class WSGIApplication(object):
    """This is a standart test class"""

    def __init__(self, options=None):
        self.options = bootstrap_defaults(options)
        #expose.options = options

    def __call__(self, environ, start_response):

        return self.static_or_dynamic(environ, start_response)

    def dynamic_handler(self, environ, start_response):

        from astrid.app.local import local
        local.initialize(environ, encoding='utf8', options=self.options)

        try:
            response = expose.run_dispatcher(self.options)
        except (HTTPError, HTTPRedirect, HTTPJSONResponse) as http_except:  # we handle http error

            if isinstance(http_except, HTTPJSONResponse):  # can handle HTTPJSONResponse
                response = http_except.render()
            elif 400 <= http_except.status_code <= 505:
                if http_except.status_code in self.options['error_pages']:  # custom error pages
                    response = local.response
                    url_error = self.options['error_pages'][http_except.status_code]
                    response.redirect(url_error, 303)
                else:
                    response = http_error(http_except.status_code)
            elif 300 <= http_except.status_code <= 310:
                response = local.response
                response.redirect(http_except.absolute_url, http_except.status_code)

        return response.__call__(start_response)

    def static_handler(self, environ, start_response, static_match):

        version, filename = static_match.group('v','f')
        response = stream_file_handler(environ, start_response, filename, version=version, options=self.options)

        return response.__call__(start_response)

    def static_or_dynamic(self, environ, start_response):

        path_info = environ['PATH_INFO']
        static_match = REGEX_STATIC.match(path_info)

        if static_match: # check if visitor has requested a static file
            return self.static_handler(environ, start_response, static_match)
        else: # else call the dynamic handler
            return self.dynamic_handler(environ, start_response)

