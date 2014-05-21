#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import copy
import datetime

REGEX_PYTHON_KEYWORDS = re.compile('^(and|del|from|not|while|as|elif|global|or|with|assert|else|if|pass|yield|break|'
                                   'except|import|print|class|exec|in|raise|continue|finally|is|return|def|'
                                   'for|lambda|try)$')

DEFAULTLENGTH = {'string': 512,
                 'password': 512,
                 'upload': 512,
                 'text': 2**15,
                 'blob': 2**31}

DEFAULT = lambda: 0


class Field(object):
    """
    Represents a database field

    Example:
        Usage::

            a = Field(name, 'string', length=32, default=None, required=False,
                requires=IS_NOT_EMPTY(),
                notnull=False, unique=False,
                widget=None, label=None, comment=None,
                writable=True, readable=True, update=None
                )
    """

    def __init__(self,
                 fieldname,
                 type='string',
                 length=None,
                 default=DEFAULT,
                 required=False,
                 requires=DEFAULT,
                 widget=None,
                 label=None,
                 comment=None,
                 writable=True,
                 readable=True,
                 compute=None,
                 update=None,
                 map_none=None,
                 ):

        if isinstance(fieldname, unicode):
            try:
                fieldname = str(fieldname)
            except UnicodeEncodeError:
                raise SyntaxError('Field: invalid unicode field name')
        self.name = fieldname
        if not isinstance(fieldname, str) or \
                fieldname[0] == '_' or '.' in fieldname or \
                REGEX_PYTHON_KEYWORDS.match(fieldname):
            raise SyntaxError('Field: invalid field name: %s, '
                              'use rname for "funny" names' % fieldname)

        if not isinstance(type, Field):
            self.type = type
        else:
            self.type = 'reference %s' % type

        self.length = length if not length is None else DEFAULTLENGTH.get(self.type, 512)
        self.default = default if default != DEFAULT else (update or None)
        self.required = required  # is this field required
        self.widget = widget
        self.comment = comment
        self.writable = writable
        self.readable = readable
        self.update = update
        self.compute = compute
        self.label = (label if label is not None else
                      fieldname.replace('_', ' ').title())
        self.requires = requires if requires is not None else []
        self.map_none = map_none

    def set_attributes(self, *args, **attributes):
        self.__dict__.update(*args, **attributes)

    def clone(self, point_self_references_to=False, **args):
        field = copy.copy(self)
        if point_self_references_to and \
                field.type == 'reference %s'+field._tablename:
            field.type = 'reference %s' % point_self_references_to
        field.__dict__.update(args)
        return field

    def formatter(self, value):
        requires = self.requires
        if value is None or not requires:
            return value or self.map_none
        if not isinstance(requires, (list, tuple)):
            requires = [requires]
        elif isinstance(requires, tuple):
            requires = list(requires)
        else:
            requires = copy.copy(requires)
        requires.reverse()
        for item in requires:
            if hasattr(item, 'formatter'):
                value = item.formatter(value)
        return value

    def validate(self, value):
        if not self.requires or self.requires == DEFAULT:
            return ((value if value != self.map_none else None), None)
        requires = self.requires
        if not isinstance(requires, (list, tuple)):
            requires = [requires]
        for validator in requires:
            (value, error) = validator(value)
            if error:
                return (value, error)
        return ((value if value != self.map_none else None), None)

    def as_dict(self, flat=False, sanitize=True):
        attrs = ('name', 'authorize', 'represent', 'ondelete',
                 'custom_store', 'autodelete', 'custom_retrieve',
                 'filter_out', 'uploadseparate', 'widget', 'uploadfs',
                 'update', 'custom_delete', 'uploadfield', 'uploadfolder',
                 'custom_qualifier', 'unique', 'writable', 'compute',
                 'map_none', 'default', 'type', 'required', 'readable',
                 'requires', 'comment', 'label', 'length', 'notnull',
                 'custom_retrieve_file_properties', 'filter_in')
        serializable = (int, long, basestring, float, tuple,
                        bool, type(None))

        def flatten(obj):
            if isinstance(obj, dict):
                return dict((flatten(k), flatten(v)) for k, v in obj.items())
            elif isinstance(obj, (tuple, list, set)):
                return [flatten(v) for v in obj]
            elif isinstance(obj, serializable):
                return obj
            elif isinstance(obj, (datetime.datetime,
                                  datetime.date, datetime.time)):
                return str(obj)
            else:
                return None

        d = dict()
        if not (sanitize and not (self.readable or self.writable)):
            for attr in attrs:
                if flat:
                    d.update({attr: flatten(getattr(self, attr))})
                else:
                    d.update({attr: getattr(self, attr)})
            d["fieldname"] = d.pop("name")
        return d

    def __nonzero__(self):
        return True

    def __str__(self):
        try:
            return '%s.%s' % (self.tablename, self.name)
        except:
            return '<no table>.%s' % self.name
