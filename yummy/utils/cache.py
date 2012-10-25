from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache

from yummy import conf


def get_cached_model(model, pk, timeout=conf.CACHE_TIMEOUT):
    if not isinstance(model, ContentType):
        model_ct = ContentType.objects.get_for_model(model)
    else:
        model_ct = model

    key = "%s:%s" % (conf.CACHE_PREFIX, pk)

    obj = cache.get(key)
    if obj is None:
        obj = model_ct.model_class()._default_manager.get(pk=pk)
        cache.set(key, obj, timeout)
    return obj

