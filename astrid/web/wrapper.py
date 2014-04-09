import sys
import inspect
import traceback


__all__ = ['ContextManager', 'WrapWithContextManager']


class ContextManager(object):
    name = 'ContextManager'
    def on_start(self): pass
    def on_success(self): pass
    def on_failure(self): pass
    def wrap_call(self, func): return func


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


class TransactDAL(ContextManager):
    def __init__(self, db):
        self.db = db
        self.name = 'TransactDAL'

    def on_start(self):
        self.db._adapter.reconnect()

    def on_success(self):
        self.db.commit()
        self.db._adapter.close()

    def on_failure(self):
        self.db.rollback()
        self.db._adapter.close()


def smart_traceback():
    tb = traceback.format_exc()
    frames = []
    for item in inspect.trace():
        frame = item[0]
        try:
            with open(frame.f_code.co_filename,'rb') as file:
                content = file.read()
        except IOError:
            content = '<unavailable>'
        frames.append(dict(filename = frame.f_code.co_filename,
                           content = content,
                           line_number = frame.f_lineno,
                           locals_variables = frame.f_locals,
                           global_variables = frame.f_globals))
    return (tb, frames)

#def example():
#
#    class CleanerExample(Cleaner):
#        def __init__(self): sys.stdout.write('connecting\n')
#        def on_start(self): sys.stdout.write('pool connection\n')
#        def on_success(self): sys.stdout.write('commit\n')
#        def on_failure(self): sys.stdout.write('rollback\n')
#        def insert(self,**data): sys.stdout.write('inserting %s\n' % data)
#
#    db = CleanerExample()
#
#    @WrapWithCleaners((db,))
#    def action(x):
#        db.insert(key=1/x)
#        return
#
#    try:
#        a = action(1)
#        a = action(0)
#    except:
#        pass # print smart_traceback()[1][-1]
