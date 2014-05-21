#!/usr/bin/env python
# -*- coding: utf-8 -*-


__all__ = ['ContextManager', 'WrapWithContextManager']


class ContextManager(object):
    name = 'ContextManager'

    def on_start(self):
        pass

    def on_success(self):
        pass

    def on_failure(self):
        pass

    def wrap_call(self, func):
        return func


class WrapWithContextManager(object):
    def __init__(self, context=[], skip_list=None):
        self.context = context
        if skip_list is None:
            skip_list = []
        self.skip_list = skip_list
    def __call__(self, f):
        def wrap(f, context):
            def g(*a, **b):
                try:
                    context.on_start()
                    output = context.wrap_call(f)(*a, **b)
                    context.on_success()
                    return output
                except:
                    context.on_failure()
                    raise
            return g
        def wrap_skip_context(f, context):
            def g(*a, **b):
                output = context.wrap_call(f)(*a, **b)
                return output
            return g
        for context in self.context:
            if isinstance(context, ContextManager):
                if context.name in self.skip_list:
                    f = wrap_skip_context(f, context)
                else:
                    f = wrap(f, context)
        return f
