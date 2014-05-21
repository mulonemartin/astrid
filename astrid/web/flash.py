#!/usr/bin/env python
# -*- coding: utf-8 -*-

from astrid.http.cookies import HTTPCookie
from astrid.html.helpers import xmlescape


class BaseCookieManager(object):
    """Flash Manager"""

    def __init__(self, options):
        """ Init """
        self.options = options

    def set(self, key, value):
        """ Seteamos un valor a la cookie, """

        from astrid.app.local import local

        options = self.options
        request = local.request
        response = local.response

        c = HTTPCookie(
            key,
            value=value,
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
        flash_cookie = request.cookies.get(key, None)

        return flash_cookie

    def delete(self, key):

        from astrid.app.local import local

        response = local.response
        options = self.options
        request = local.request

        response.cookies.append(HTTPCookie.delete(
                key,
                path=request.root_path + options.get('AUTH_COOKIE_PATH'),
                options=options))


class FlashManager(BaseCookieManager):
    """Flash Manager"""

    cookie_name = 'flash_alert'
    message = ''
    type = 'info'
    div_char = '|' #'\x1f'

    def encode(self, message, type):
        return self.div_char.join([type, message])

    def decode(self, encode):
        return encode.split(self.div_char, 1)

    def save(self, message='', type='info'):
        self.message = message
        self.type = type
        enc_msg = self.encode(message, type)
        self.set(self.cookie_name, enc_msg)

    def load(self):
        enc_msg = self.get(self.cookie_name)
        if enc_msg:
            try:
                self.type, self.message = self.decode(enc_msg)
            except ValueError:
                self.type = 'info'
                self.message = self.decode(enc_msg)


    def info(self, message=''):
        self.save(message, type='info')

    def warning(self, message=''):
        self.save(message, type='warning')

    def error(self, message=''):
        self.save(message, type='error')

    def success(self, message=''):
        self.save(message, type='success')

    def render(self):
        self.load()
        self.delete(self.cookie_name)
        if self.message != "":
            if self.type in ['info']:
                return self.render_type('info')
            elif self.type in ['warning']:
                return self.render_type('block')
            elif self.type in ['error']:
                return self.render_type('error')
            elif self.type in ['success']:
                return self.render_type('success')
        else:
            return ''

    #def render_type(self, render_class):
    #
    #    xml = '''
    #    <div class="alert alert-%(render_class)s">
    #        <button type="button" class="close" data-dismiss="alert">&times;</button>
    #        <h4>%(title)s!</h4>
    #        %(message)s
    #    </div>
    #    ''' % {'render_class': render_class,
    #           'title': self.type.capitalize(),
    #           'message': xmlescape(self.message)}
    #
    #    return xml

    def render_type(self, render_class):
        """Only work using twitter bootstrap, see: http://getbootstrap.com"""

        xml = '''
        <div class="alert alert-%(render_class)s">
            <button type="button" class="close" data-dismiss="alert">&times;</button>
            %(message)s
        </div>
        ''' % {'render_class': render_class,
               'message': xmlescape(self.message)}

        return xml


    def render_dialog(self):
        """Only work using twitter bootstrap, see: http://getbootstrap.com"""

        self.load()
        self.delete(self.cookie_name)
        if self.message != "":
            style = 'background-color: #428BCA; color: #fff;'
            if self.type in ['info']:
                style = 'background-color: #428BCA; color: #fff;'
            elif self.type in ['warning']:
                style = 'background-color: #c09853; color: #fff;'
            elif self.type in ['error']:
                style = 'background-color: #b94a48; color: #fff;'
            elif self.type in ['success']:
                style = 'background-color: #468847; color: #fff;'

            xml = '''
            <!-- Modal -->
            <div class="modal fade" id="AstridShowAlertModal" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header" style="%(style)s">
                            <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
                            <div style="height: 22px;"></div>
                        </div>
                        <div class="modal-body showalertmodal-body">

                            %(message)s

                        </div>
                        <div class="modal-footer">
                            <a class="btn btn-primary" href="#" data-dismiss="modal" aria-hidden="true">OK</a>
                        </div>
                    </div><!-- /.modal-content -->
                </div><!-- /.modal-dialog -->
            </div><!-- /.modal -->
            <script>
            $(document).ready(function() {
                $('#AstridShowAlertModal').modal({
                        keyboard: false
                    });

            });
            </script>
            ''' % {
                'message': xmlescape(self.message),
                'style': style
            }
            return xml
        else:
            return ''



