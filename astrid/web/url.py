#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib


def url(*args, **kwargs):
    """Url make"""

    func_par = args
    if 'args' in kwargs:
        func_args = kwargs['args']
    else:
        func_args = None

    if 'vars' in kwargs:
        func_vars = kwargs['vars']
    else:
        func_vars = None

    if func_args in (None, []):
        func_args = []

    if not func_par:
        raise SyntaxError("You need to pass at least one argument")

    func_vars = func_vars or {}

    if not isinstance(func_par, (list, tuple)):
        func_par = [func_par]

    if not isinstance(func_args, (list, tuple)):
        func_args = [func_args]

    if func_args:
        other = func_args and urllib.quote(
                '/' + '/'.join([str(x) for x in func_args]))
    else:
        other = ''

    if other.endswith('/'):
        other += '/'    # add trailing slash to make last trailing empty arg explicit

    list_vars = []
    for (key, vals) in sorted(func_vars.items()):
        if not isinstance(vals, (list, tuple)):
            vals = [vals]
        for val in vals:
            list_vars.append((key, val))

    if list_vars:
        other += '?%s' % urllib.urlencode(list_vars)

    func_and_par = func_par and urllib.quote(
        '/' + '/'.join([str(x) for x in func_par]))

    func_and_par = func_and_par.replace('//', '/')

    return func_and_par + other

