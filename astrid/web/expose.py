#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging

from astrid.app.local import local
from astrid.web.wrapper import WrapWithContextManager
from astrid.http.response import not_found, internal_error
from astrid.app.logger import logging
from astrid.web.url import url
from astrid.routing.router import PathRouter
from astrid.http.response import JSONResponse, HTTPResponse, HTTPError


__all__ = ['expose']


class expose(object):
    """ This expose a function as controller """

    common_contexts = []
    routes_error = {}
    options = None
    router = PathRouter()


    def __init__(self,
                 path = None,
                 name = None,
                 template = None,
                 contexts = None,
                 skip_list = None
                 ):
        if callable(path):
            raise SyntaxError('@expose(), not @expose')

        self.path = path
        self.name = name
        self.template = template
        self.contexts = self.common_contexts + (contexts or [])
        self.skip_list = skip_list

    def __call__(self, func):

        self.func_name = func.__name__
        self.filename = func.__code__.co_filename
        self.mtime = os.path.getmtime(self.filename)

        if not self.path:
            self.path = '/' + func.__name__ + '(.\w+)?'
        if not self.name:
            self.name = self.func_name
        if not self.path.startswith('/'):
            self.path = '/' + self.path
        if not self.path.endswith('/'):
            self.path = self.path + '/'
        if not self.template:
            self.template = self.func_name + '.html'

        wrapped_func = WrapWithContextManager(self.contexts, skip_list=self.skip_list)(func)
        self.func = wrapped_func
        self.router.add_route(self.path, self, name=self.name)

        logging.info("  exposing '%s' as '%s'" % (self.name, self.path))

        return func

    @staticmethod
    def run_dispatcher(options):
        " maps the path_info into a function call "

        request = local.request
        response = local.response

        output = None
        is_match = False
        if not request.path.endswith('/'):
            request.path = request.path + '/'
        match_obj, match_dict = expose.router.match(request.path)
        if match_obj:
            try:
                del match_dict['route_name']  #remove route_name key from dictionary
            except KeyError:
                pass

            output = match_obj.func(**match_dict)
            is_match = True

        if not output:
            raise HTTPError(404)
            #return not_found()

        if isinstance(output, HTTPResponse):
            return output
        elif isinstance(output, basestring):
            # render simple base string
            response.write(output)
            return response
        elif isinstance(output, dict):
            # So this render template
            if not 'app_local' in output:
                output['app_local'] = local

            output['flash'] = local.flash  # flash alert
            output['url'] = url  # pass url function to the template

            if match_obj.template.startswith('/'):
                template_path = match_obj.template[1:]
            else:
                template_path = match_obj.template

            filename = os.path.join(
                            options['TEMPLATES_FOLDER'], template_path)

            if os.path.exists(filename):
                output = options['render_template'](filename = match_obj.template,
                                            path = options['TEMPLATES_FOLDER'],
                                            context = output)

                if options['SERVER'] in ['wsgiref']:  # wsgiref only support utf-8
                    response.write(output.encode('utf-8'))
                else:
                    response.write(output)
                return response
            else:
                logging.error("Template file doesn't exist")

        elif isinstance(output, JSONResponse):
            # Render if is json data
            return output.render()
        else:
            logging.error("The function need to return data type of: string / dict() or JSONResponse")
            raise HTTPError(500)
