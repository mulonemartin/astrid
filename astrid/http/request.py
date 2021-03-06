
""" ``request`` module.
"""

from astrid.core.descriptors import attribute
from astrid.core.url import UrlParts

from astrid.http.comp import bton
from astrid.http.comp import parse_qs
from astrid.core.parse import parse_cookie
from astrid.core.parse import parse_multipart
from astrid.core.json import json_decode


class HTTPRequest(object):
    """ Represent HTTP request. ``environ`` variables
        are accessable via attributes.

        >>> from wheezy.core.collections import last_item_adapter
        >>> from wheezy.http.config import bootstrap_http_defaults
        >>> from wheezy.http.tests import sample
        >>> environ = {
        ...         'SCRIPT_NAME': '/abc',
        ...         'PATH_INFO': '/de',
        ...         'QUERY_STRING': 'a=1&a=2&b=3'
        ... }
        >>> options = {}
        >>> bootstrap_http_defaults(options)
        >>> sample.request(environ)
        >>> sample.request_headers(environ)
        >>> r = HTTPRequest(environ, encoding='utf8', options=options)
        >>> r.method
        'GET'
        >>> r.root_path
        '/abc/'
        >>> r.path
        '/abc/de'
        >>> r.query['a']
        ['1', '2']
        >>> query = last_item_adapter(r.query)
        >>> query['a']
        '2'

        Return the originating host of the request.

        >>> environ['HTTP_HOST'] = 'example.com'
        >>> r = HTTPRequest(environ, encoding='utf8', options=options)
        >>> r.host
        'example.com'

        If the host is behind multiple proxies, return
        the last one.

        >>> environ['HTTP_HOST'] = 'a, b, python.org'
        >>> r = HTTPRequest(environ, encoding='utf8', options=options)
        >>> r.host
        'python.org'

        Return the originating ip address of the request.

        >>> environ['REMOTE_ADDR'] = '7.1.3.2'
        >>> r = HTTPRequest(environ, encoding='utf8', options=options)
        >>> r.remote_addr
        '7.1.3.2'

        If the remote client is behind multiple proxies,
        return the fist one.

        >>> r = HTTPRequest(environ, encoding='utf8', options=options)
        >>> environ['REMOTE_ADDR'] = 'a, b, c'
        >>> r.remote_addr
        'a'

        Cookies:

        >>> r.cookies
        {}
        >>> r = HTTPRequest(environ, encoding='utf8', options=options)
        >>> environ['HTTP_COOKIE'] = 'ID=1234; PREF=abc'
        >>> cookies = r.cookies
        >>> cookies['ID']
        '1234'

        Check if http request is secure (HTTPS)

        >>> r.secure
        False
        >>> r.scheme
        'http'
        >>> r = HTTPRequest(environ, encoding='utf8', options=options)
        >>> environ['wsgi.url_scheme'] = 'https'
        >>> r.secure
        True
        >>> r.scheme
        'https'

        Check if http request is ajax request

        >>> r.ajax
        False

        >>> r = HTTPRequest(environ, encoding='utf8', options=options)
        >>> environ['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'
        >>> r.ajax
        True

        >>> r = HTTPRequest(environ, encoding='utf8', options=options)
        >>> r.urlparts
        urlparts('https', 'python.org', '/abc/de', 'a=1&a=2&b=3', None)
        >>> r.urlparts.geturl()
        'https://python.org/abc/de?a=1&a=2&b=3'
    """

    def __init__(self, environ, encoding, options):
        self.environ = environ
        self.encoding = encoding
        self.options = options
        self.method = environ['REQUEST_METHOD']

    @attribute
    def host(self):
        host = self.environ['HTTP_HOST']
        if ',' in host:
            host = host.rsplit(',', 1)[-1].strip()
        return host

    @attribute
    def remote_addr(self):
        """
        POSIBLE IMPLEMENTACION PARA TENER EN CUENTA PROXY

        if request.META.has_key("HTTP_X_FORWARDED_FOR"):
            request.META["HTTP_X_PROXY_REMOTE_ADDR"] = request.META["REMOTE_ADDR"]
            parts = request.META["HTTP_X_FORWARDED_FOR"].split(",", 1)
            request.META["REMOTE_ADDR"] = parts[0]

        O ASI MAS CLARO:

        if 'HTTP_X_FORWARDED_FOR' in request.META:
            ip_adds = request.META['HTTP_X_FORWARDED_FOR'].split(",")
            ip = ip_adds[0]
        else:
            ip = request.META['REMOTE_ADDR']


        def get_client(env):
            guess the client address from the environment variables
            first tries 'http_x_forwarded_for', secondly 'remote_addr'
            if all fails, assume '127.0.0.1' or '::1' (running locally)

            g = regex_client.search(env.get('http_x_forwarded_for', ''))
            client = (g.group() or '').split(',')[0] if g else None
            if client in (None, '', 'unkown'):
                g = regex_client.search(env.get('remote_addr', ''))
                if g:
                    client = g.group()
                elif env.http_host.startswith('['):  # IPv6
                    client = '::1'
                else:
                    client = '127.0.0.1'  # IPv4
            if not is_valid_ip_address(client):
                raise HTTP(400, "Bad Request (request.client=%s)" % client)
            return client

        """

        addr = self.environ['REMOTE_ADDR']
        if ',' in addr:
            addr = addr.split(',', 1)[0].strip()
        return addr

    @attribute
    def remote_addr_x_real(self):
        """What key error"""

        addr = self.environ['HTTP_X_REAL_IP']
        if ',' in addr:
            addr = addr.split(',', 1)[0].strip()
        return addr

    @attribute
    def root_path(self):
        return self.environ['SCRIPT_NAME'] + '/'

    @attribute
    def path(self):
        return self.environ['SCRIPT_NAME'] + self.environ['PATH_INFO']

    @attribute
    def query(self):
        return parse_qs(
            self.environ['QUERY_STRING'],
            encoding=self.encoding
        )

    @attribute
    def form(self):
        form, self.files = self.load_body()
        return form

    @attribute
    def files(self):
        self.form, files = self.load_body()
        return files

    @attribute
    def cookies(self):
        if 'HTTP_COOKIE' in self.environ:
            return parse_cookie(self.environ['HTTP_COOKIE'])
        else:
            return {}

    @attribute
    def ajax(self):
        if 'HTTP_X_REQUESTED_WITH' in self.environ:
            return self.environ['HTTP_X_REQUESTED_WITH'] == 'XMLHttpRequest'
        else:
            return False

    @attribute
    def secure(self):
        return self.environ['wsgi.url_scheme'] == 'https'

    @attribute
    def scheme(self):
        return self.environ['wsgi.url_scheme']

    @attribute
    def urlparts(self):
        return UrlParts((self.scheme, self.host,
                         self.path, self.environ['QUERY_STRING'], None))

    def load_body(self):
        """ Load http request body and returns
            form data and files.

            >>> from wheezy.core.collections import last_item_adapter
            >>> from wheezy.http.config import bootstrap_http_defaults
            >>> from wheezy.http.tests import sample
            >>> environ = {}
            >>> options = {}
            >>> bootstrap_http_defaults(options)
            >>> sample.request(environ)

            Load form as application/x-www-form-urlencoded

            >>> sample.request_urlencoded(environ)
            >>> r = HTTPRequest(environ, encoding='utf8', options=options)
            >>> assert len(r.form) == 2
            >>> r.form['greeting']
            ['Hello World', 'Hallo Welt']
            >>> form = last_item_adapter(r.form)
            >>> form['greeting']
            'Hallo Welt'
            >>> assert r.files is None

            Load form as multipart/form-data.

            >>> sample.request_multipart(environ)
            >>> r = HTTPRequest(environ, encoding='utf8', options=options)
            >>> assert len(r.form) == 1
            >>> assert len(r.files) == 1

            Load files first this time

            >>> sample.request_multipart(environ)
            >>> r = HTTPRequest(environ, encoding='utf8', options=options)
            >>> assert len(r.files) == 1
            >>> assert len(r.form) == 1

            Content-Length exceed maximum allowed

            >>> cl = options['MAX_CONTENT_LENGTH'] + 1
            >>> environ['CONTENT_LENGTH'] = str(cl)
            >>> r = HTTPRequest(environ, encoding='utf8', options=options)
            >>> r.load_body() # doctest: +ELLIPSIS
            Traceback (most recent call last):
                ...
            ValueError: ...
        """
        environ = self.environ
        cl = environ['CONTENT_LENGTH']
        icl = int(cl)
        if icl > self.options['MAX_CONTENT_LENGTH']:
            raise ValueError('Maximum content length exceeded')
        fp = environ['wsgi.input']
        ct = environ['CONTENT_TYPE']
        if ct.startswith('m'):
            return parse_multipart(fp, ct, cl, self.encoding)
        else:
            qs = bton(fp.read(icl), self.encoding)
            return parse_qs(qs, self.encoding), None


    def json_from_body(self):
        """ Cargamos el json del body y lo retornamos en formato json"""

        environ = self.environ
        cl = environ['CONTENT_LENGTH']
        icl = int(cl)
        if icl > self.options['MAX_CONTENT_LENGTH']:
            raise ValueError('Maximum content length exceeded')
        fp = environ['wsgi.input']
        ct = environ['CONTENT_TYPE']
        if ct.startswith('m'):
            raise ValueError("No se aceptan contenidos POST: multipart para JSON")
        else:
            json_string = bton(fp.read(icl), self.encoding)
            json_in = json_decode(json_string)
            return json_in

