from collections import namedtuple
from django.conf import settings
from django.utils.translation import npgettext, ugettext_lazy as _

Unit = namedtuple('Unit', 'id name abbr')
UNITS = (
    Unit(0, npgettext('unit', 'piece', 'pieces', 1), npgettext('unit', 'pc', 'pcs', 1)),
    Unit(1, npgettext('unit', 'gram', 'grams', 1), 'g'),
    Unit(2, npgettext('unit', 'dekagram', 'dekagrams', 1), 'dkg'),
    Unit(3, npgettext('unit', 'kilogram', 'kilograms', 1), 'kg'),
    Unit(4, npgettext('unit', 'mililiter', 'mililiters', 1), 'ml'),
    Unit(5, npgettext('unit', 'deciliter', 'deciliters', 1), 'dl'),
    Unit(6, npgettext('unit', 'liter', 'liters', 1), 'l'),
    Unit(100, npgettext('unit', 'cup', 'cups', 1), npgettext('unit', 'cup', 'cups', 1)),
)
UNIT_CHOICES = tuple(unit[:2] for unit in UNITS)


PRICING_CHOICES = (
    (1, _('Cheapest')),
    (2, _('Cheaper')),
    (3, _('Standard price')),
    (4, _('Expensive')),
    (5, _('Most Expensive')),
)

DIFFICULTY_CHOICES = (
    (1, _('Easy')),
    (3, _('Standard difficulty')),
    (5, _('Difficult')),
)

PHOTO_EXTENSION = {
    'JPEG': '.jpg',
    'PNG': '.png',
    'GIF': '.gif'
}

RECIPE_RECOMMENDATIONS_COUNT = 3

CATEGORY_ORDER_DEFAULT = getattr(settings, 'YUMMY_CATEGORY_ORDER', '-created')
CATEGORY_ORDERING = {
    'slug': _("by ranking"),  # TODO - add ranking
    'title': _("by alphabet"),
    '-created': _("by date"),
}
CATEGORY_PHOTO_OPTIONS = ('all', 'photos')
CATEGORY_ORDER_ATTR = 'category_order_attr'
CATEGORY_PHOTO_ATTR = 'category_photo_attr'
