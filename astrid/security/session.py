#!/usr/bin/env python
# -*- coding: utf-8 -*-

from astrid.http.cookies import HTTPCookie


class SessionManager(object):
    """Session Manager"""

    def __init__(self, options):
        """ Init """
        self.options = options
        self.ticket = options.get('ticket')

    def set(self, key, value):
        """ Seteamos un valor a la cookie, """

        from astrid.app.local import local

        options = self.options
        request = local.request
        response = local.response

        c = HTTPCookie(
                        key,
                        value=self.ticket.encode(value),
                        path=request.root_path + options.get('AUTH_COOKIE_PATH'),
                        domain=options.get('AUTH_COOKIE_DOMAIN'),
                        secure=options.get('AUTH_COOKIE_SECURE'),
                        httponly=True,
                        options=options
                        )
        response.cookies.append(c)

    def get(self, key):
        """ Obtenemos el valor de la key """

        from astrid.app.local import local

        request = local.request

        session_cookie = request.cookies.get(key, None)
        if session_cookie is not None:
            ticket, time_left = self.ticket.decode(session_cookie)
            if ticket:
                return ticket
        return None

    def time_left(self, key):
        """Cuanto falta para"""

        from astrid.app.local import local

        request = local.request

        session_cookie = request.cookies.get(key, None)
        if session_cookie is not None:
            ticket, time_left = self.ticket.decode(session_cookie)
            return time_left
        return None