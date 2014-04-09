#!/usr/bin/env python
# -*- coding: utf-8 -*-

#You don't have to do this two lines if you are using in production trought pypi.
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))


from astrid.web.wsgi import WSGIApplication
from astrid.http.server import run
from astrid.web.expose import expose


@expose()
def index():
    message = "This is a test"
    return dict(message=message)


@expose('edit/{id:int}', template='index.html')
def edit(id):
    message = "Args id: %s" % id
    return dict(message=message)


@expose('post/{year:int}/{month:int}', template='index.html')
def post(year, month):
    message = "Args year: %s, month: %s" % (year, month)
    return dict(message=message)


@expose('translation/{locale:(en|ru)}', template='index.html')
def translation(locale):
    message = "Args locale: %s" % locale
    return dict(message=message)


@expose('crud/{action:(add|edit|remove)}/{id:int}', template='index.html')
def crud(action, id):
    message = "Args action: %s, id: %s" % (action, id)
    return dict(message=message)


@expose('something/{any:any}', template='index.html')
def something(any):
    message = "Args any: %s" % any
    return dict(message=message)



if __name__ == '__main__':
    options = {
        'SERVER': 'wsgiref',
        'IP': '0.0.0.0',
        'PORT': 8000,
        'TEMPLATES_FOLDER': 'templates/',
        'STATIC_FOLDER': os.path.abspath('../static')
    }
    app = WSGIApplication(options)
    run(app, server=options['SERVER'], host=options['IP'], port=options['PORT'])

