from functools import wraps

from django.core.cache import cache

from yummy import conf


def recached_method_to_mem(func):
    @wraps(func)
    def wrapped_func(self, recache=False):
        attr_name = '_%s' % func.__name__
        if not hasattr(self, attr_name) or recache:
            res = func(self, recache=recache)
            setattr(self, attr_name, res)
        return getattr(self, attr_name)

    return wrapped_func


def cache_method_with_obj(func):
    @wraps(func)
    def new_func(self, obj):
        key = self.__class__.cache_manager_key(func.__name__, obj)
        res = cache.get(key)
        if res is None:
            res = list(func(self, obj))
            cache.set(key, res, timeout=conf.CACHE_TIMEOUT)
        return res

    return new_func


def add_cached_methods(cls):

    for method in cls.CACHE_METHODS:
        cached_method = '%s_cached' % method
        setattr(cls, cached_method, cache_method_with_obj(getattr(cls, method)))
    return cls
