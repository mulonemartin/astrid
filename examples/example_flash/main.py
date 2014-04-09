#!/usr/bin/env python
# -*- coding: utf-8 -*-

#You don't have to do this two lines if you are using in production trought pypi.
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))


from astrid.web.wsgi import WSGIApplication
from astrid.http.server import run
from astrid.web.expose import expose
from astrid.http.response import HTTPError, HTTPRedirect
from astrid.app.local import local
from astrid.web.url import url


@expose()
def index():
    message = "This is index"
    return dict(message=message)


@expose()
def info():
    local.flash.info('Hey this a flash message, some body text here please, need more content')
    raise HTTPRedirect(url('index'))


@expose()
def warning():
    local.flash.warning('Hey this a flash message, some body text here please, need more content')
    raise HTTPRedirect(url('index'))


@expose()
def error():
    local.flash.error('Hey this a flash message, some body text here please, need more content')
    raise HTTPRedirect(url('index'))


@expose()
def success():
    local.flash.success('Hey this a flash message, some body text here please, need more content')
    raise HTTPRedirect(url('index'))


if __name__ == '__main__':
    options = {
        'TEMPLATES_FOLDER': 'templates/',
        'STATIC_FOLDER': os.path.abspath('../static')
    }
    app = WSGIApplication(options)
    run(app)

