from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module


def import_module_member(modstr):
    try:
        mod_path, attr = modstr.rsplit('.', 1)
        mod = import_module(mod_path)
        member = getattr(mod, attr)
    except (AttributeError, ImportError, ValueError), e:
        raise ImproperlyConfigured('Error importing %s: "%s"' % (modstr, e))
    else:
        return member
