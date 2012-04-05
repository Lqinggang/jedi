import inspect

NOTICE = object()
WARNING = object()
ERROR = object()

def dbg(*args):
    if debug_function:
        frm =  inspect.stack()[1]
        mod = inspect.getmodule(frm[0])
        if not (mod.__name__ in ignored_modules):
            debug_function(NOTICE, *args)

def warning(*args):
    if debug_function:
        debug_function(WARNING, *args)

def error(*args):
    if debug_function:
        debug_function(ERROR, *args)

def print_to_stdout(level, *args):
    """ The default debug function """
    print 'dbg:' if level == NOTICE else 'warning:', args

debug_function = None
ignored_modules = []
