#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading

from astrid.http.response import HTTPResponse
from astrid.http.request import HTTPRequest
from astrid.security.session import SessionManager
from astrid.web.flash import FlashManager


__all__ = ['local']



class LocalThread(threading.local):

    def initialize(self, environ, encoding='utf8', options=None):
        self.__dict__.clear()
        self.environ = environ
        self.request = HTTPRequest(environ, encoding=encoding, options=options)
        self.response = HTTPResponse(options['CONTENT_TYPE'], options['ENCODING'])
        #self.session = SessionManager(options)
        self.options = options
        self.flash = FlashManager(options)


local = LocalThread()