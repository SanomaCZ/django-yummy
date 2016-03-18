from django.core.exceptions import ImproperlyConfigured

try:
    from importlib import import_module
except ImportError:
    from django.utils.importlib import import_module

try:
    from django.apps import apps
except ImportError:  # django < 1.7
    from django.db.models.loading import get_model
else:
    get_model = apps.get_model


def import_module_member(modstr):
    try:
        mod_path, attr = modstr.rsplit('.', 1)
        mod = import_module(mod_path)
        member = getattr(mod, attr)
    except (AttributeError, ImportError, ValueError), e:
        raise ImproperlyConfigured('Error importing %s: "%s"' % (modstr, e))
    else:
        return member
