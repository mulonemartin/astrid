#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os


class BaseTemplate(object):
    def render(self, filename, path, context):
        return "Nothing"


class Web2pyTemplate(BaseTemplate):
    def __call__(self, filename, path, context):
        from giweb.html.ext.web2py_template import render
        return render(filename=filename,
                        path=path,
                        context=context)


class MakoTemplate(BaseTemplate):
    def __init__(
            self,
            directories=None,
            module_directory='/tmp/mako_modules',
            **kwargs):

        from mako.lookup import TemplateLookup
        self.template_lookup = TemplateLookup(
            directories=directories or ['/media/sf_Proyectos/web2py/web3py/apps/test_mako/templates/'],
            module_directory=module_directory,
            **kwargs)

    def __call__(self, filename, path, context):
        filepath, file = os.path.split(filename)
        template = self.template_lookup.get_template(filename)
        return template.render(**context)
        #return template.render_unicode(**context).encode('utf-8', 'replace')


class TenjinTemplate(object):
    """ Integration with Tenjin templates.
    """
    __slots__ = ('engine', 'helpers')

    def __init__(
            self, path=None, pp=None, helpers=None,
            encoding='UTF-8', postfix='.html', cache=None, **kwargs):
        import tenjin
        tenjin.set_template_encoding(encoding)
        from tenjin.helpers import capture_as, captured_as, cache_as
        try:  # pragma: nocover
            from webext import escape_html as escape
        except ImportError:  # pragma: nocover
            from tenjin.helpers import escape

        from astrid.core.comp import str_type
        self.helpers = {
            'to_str': str_type,
            'escape': escape,
            'capture_as': capture_as,
            'captured_as': captured_as,
            'cache_as': cache_as,
            'tenjin': tenjin
        }
        if helpers:
            self.helpers.update(helpers)
        self.engine = tenjin.Engine(
            path=path or ['content/templates'],
            postfix=postfix,
            cache=cache or tenjin.MemoryCacheStorage(),
            pp=pp,
            **kwargs)

    def __call__(self, template_name, kwargs):
        return self.engine.render(template_name, kwargs, self.helpers)


class Jinja2Template(object):
    """ Integration with Jinja2 templates.
    """

    def __init__(self, env):
        assert env
        self.env = env

    def __call__(self, template_name, kwargs):
        return self.env.get_template(template_name).render(kwargs)