

def recached_method_to_mem(func):
    def wrapped_func(self, recache=False):
        attr_name = '_%s' % func.__name__
        if not hasattr(self, attr_name) or recache:
            res = func(self, recache=recache)
            setattr(self, attr_name, res)
        return getattr(self, attr_name)

    wrapped_func.__dict__ = func.__dict__
    wrapped_func.__doc__ = func.__doc__
    wrapped_func.__name__ = func.__name__

    return wrapped_func
