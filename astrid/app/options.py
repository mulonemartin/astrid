#!/usr/bin/env python
# -*- coding: utf-8 -*-

from astrid.html.templates import MakoTemplate
from astrid.security.crypto import Ticket
from astrid.security.crypto.comp import aes128
from astrid.security.crypto.comp import ripemd160
from astrid.security.crypto.comp import sha1
from astrid.security.crypto.comp import sha256


def bootstrap_defaults(options):
    """ Configuration options """

    if not options:
        options = {}

    options.setdefault('ENCODING', 'UTF-8')
    options.setdefault(
        'CONTENT_TYPE', 'text/html; charset=' + options['ENCODING'])
    options.setdefault('SERVER', 'wsgiref')
    options.setdefault('IP', '127.0.0.1')
    options.setdefault('PORT', 8000)
    options.setdefault('STATIC_FOLDER', '/media/sf_Proyectos/web2py/astrid/examples/static/')
    options.setdefault('TEMPLATES_FOLDER', '/media/sf_Proyectos/web2py/astrid/examples/templates/')
    options.setdefault('render_template', MakoTemplate(options['TEMPLATES_FOLDER']))
    options.setdefault('MAX_CONTENT_LENGTH', 20000)
    options.setdefault('CUSTOM_LOAD_BODY', None)

    options.setdefault('HTTP_COOKIE_DOMAIN', None)
    options.setdefault('HTTP_COOKIE_SECURE', False)
    options.setdefault('HTTP_COOKIE_HTTPONLY', False)

    options.setdefault('AUTH_COOKIE', '_a')
    options.setdefault('AUTH_COOKIE_DOMAIN', None)
    options.setdefault('AUTH_COOKIE_PATH', '')
    options.setdefault('AUTH_COOKIE_SECURE', False)

    options.setdefault('ticket-max-age', 1200)
    options.setdefault('ticket-salt', 'WmMFkzVbSpWlAKb6cOC1')
    options.setdefault('CRYPTO_ENCRYPTION_KEY', 'r0sWsYR3dHUcxPWeecB7')
    options.setdefault('CRYPTO_VALIDATION_KEY', 'kTXdyg9ZScNyE6YKPPJU')
    options.setdefault('ticket', Ticket(
                                        max_age=options.get('ticket-max-age'),
                                        salt=options.get('ticket-salt'),
                                        cypher=aes128,
                                        digestmod=ripemd160 or sha256 or sha1,
                                        options=options))
    options.setdefault('error_pages', {})

    return options
