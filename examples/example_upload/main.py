#!/usr/bin/env python
# -*- coding: utf-8 -*-

#You don't have to do this two lines if you are using in production trought pypi.
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from uuid import uuid4

from astrid.web.wsgi import WSGIApplication
from astrid.http.server import run
from astrid.web.expose import expose
from astrid.app.local import local
from astrid.core.uuid import shrink_uuid

from astrid.html.forms import Form
from astrid.db.dal import Field
from astrid.http.response import HTTPError, HTTPRedirect


@expose()
def index():
    message = "Please upload you file"
    return dict(message=message)


@expose(template='index.html')
def upload():
    local.upload_session = shrink_uuid(uuid4())
    print local.upload_session

    form = Form(Field('upload', 'upload')).process()
    if form.accepted:
        print "Accepted"
        #print local.request.files['upload']
        raise HTTPRedirect('index')
    return dict(message=form)




if __name__ == '__main__':
    options = {
        'SERVER': 'wsgiref',
        'IP': '0.0.0.0',
        'PORT': 8000,
        'TEMPLATES_FOLDER': 'templates/',
        'STATIC_FOLDER': os.path.abspath('../static'),
        'MAX_CONTENT_LENGTH': 2000000000,
        'FORM_LOAD_BODY_LARGE': True
    }
    app = WSGIApplication(options)
    run(app, server=options['SERVER'], host=options['IP'], port=options['PORT'])

