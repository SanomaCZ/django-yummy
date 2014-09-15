from django.conf import settings
from django.utils.translation import npgettext_lazy, ugettext_lazy as _

from yummy.utils import import_module_member

# contains id of unit (used in models as choices in Choicesfield), translation function
# based npgettext_lazy, optional shortcut of unit and required form for translation if amount
# is decimal number (standard number for npgettext_lazy or char 'm' for magic transormation that use
# 1 if setting ALLOW_MAGIC_UNITS_TRANSFORM is Flase else 5 and slugify last char of returned val
# from npgettext_lazy)
UNITS = (
    (0, lambda c=1: npgettext_lazy('unit', 'piece', 'pieces', c), lambda c=1: npgettext_lazy('unit', 'pc', 'pcs', c), 'm'),
    (1, lambda c=1: npgettext_lazy('unit', 'gram', 'grams', c), 'g', 'm'),
    (2, lambda c=1: npgettext_lazy('unit', 'dekagram', 'dekagrams', c), 'dkg', 'm'),
    (3, lambda c=1: npgettext_lazy('unit', 'kilogram', 'kilograms', c), 'kg', 'm'),
    (4, lambda c=1: npgettext_lazy('unit', 'mililiter', 'mililiters', c), 'ml', 'm'),
    (5, lambda c=1: npgettext_lazy('unit', 'deciliter', 'deciliters', c), 'dl', 'm'),
    (6, lambda c=1: npgettext_lazy('unit', 'liter', 'liters', c), 'l', 'm'),
    (7, lambda c=1: npgettext_lazy('unit', 'packaging', 'packagings', c), 'pack', 1), #baleni
    (8, lambda c=1: npgettext_lazy('unit', 'package', 'packages', c), 'pkg', 'm'), #balicek
    (9, lambda c=1: npgettext_lazy('unit', 'part', 'parts', c), 'bit', 'm'), #dilek
    (10, lambda c=1: npgettext_lazy('unit', 'cup', 'cups', c), 'm'), #hrnek
    (11, lambda c=1: npgettext_lazy('unit', 'handful', 'handful', c), 2), #hrst
    (12, lambda c=1: npgettext_lazy('unit', 'drop', 'drops', c), 2), #kapka
    (13, lambda c=1: npgettext_lazy('unit', 'crubicle', 'crubicles', c), 'm'), #kelimek
    (14, lambda c=1: npgettext_lazy('unit', 'can', 'cans', c), 2), #plechovka
    (15, lambda c=1: npgettext_lazy('unit', 'scoop', 'scoops', c), 'm'), #kopecek
    (16, lambda c=1: npgettext_lazy('unit', 'cube', 'cubes', c), 2), #kostka
    (17, lambda c=1: npgettext_lazy('unit', 'ball', 'balls', c), 2), #kulicka
    (18, lambda c=1: npgettext_lazy('unit', 'bottle', 'bottles', c), 2), #lahev
    (19, lambda c=1: npgettext_lazy('unit', 'spoon', 'spoons', c), 1), #lzice
    (20, lambda c=1: npgettext_lazy('unit', 'teaspoon', 'teaspoons', c), 2), #lzicka
    (21, lambda c=1: npgettext_lazy('unit', 'bowl', 'bowls', c), 2), #miska
    (22, lambda c=1: npgettext_lazy('unit', 'bud', 'buds', c), 2), #palicka
    (23, lambda c=1: npgettext_lazy('unit', 'slice', 'slices', c), 'm'), #platek
    (24, lambda c=1: npgettext_lazy('unit', 'tin', 'tins', c), 2), #konzerva
    (25, lambda c=1: npgettext_lazy('unit', 'jar', 'jars', c), 1), #sklenice
    (26, lambda c=1: npgettext_lazy('unit', 'sprig', 'sprigs', c), 2), #snitka
    (27, lambda c=1: npgettext_lazy('unit', 'clove', 'cloves', c), 'm'), #strouzek
    (28, lambda c=1: npgettext_lazy('unit', 'bunch', 'bunches', c), 'm'), #svazek
    (29, lambda c=1: npgettext_lazy('unit', 'crumb', 'crumbs', c), 2), #spetka
    (30, lambda c=1: npgettext_lazy('unit', 'teacup', 'teacups', c), 'm'), #salek
    (31, lambda c=1: npgettext_lazy('unit', 'twig', 'twigs', c), 2), #vetvicka
    (32, lambda c=1: npgettext_lazy('unit', 'serving', 'servings', c), 1), #porce
    (33, lambda c=1: npgettext_lazy('unit', 'leaf', 'leaves', c), 'm'), #list
    (34, lambda c=1: npgettext_lazy('unit', 'microphyll', 'microphylles', c), 'm'), #listek, small leaf
    (35, lambda c=1: npgettext_lazy('unit', 'batch', 'batches', c), 2), #davka
)

UNIT_CHOICES = tuple((unit[0], unit[1]()) for unit in UNITS)

# dict consists of unit id, gettext function and form for decimal numbers of amount
DICT_UNITS = dict((unit[0], (unit[1], unit[-1])) for unit in UNITS)

# set to True if you want to get unit translation for decial amount from plural
ALLOW_MAGIC_UNITS_TRANSFORM = getattr(settings, 'YUMMY_ALLOW_MAGIC_UNITS_TRANSFORM', False)

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
    'by_rating': _("by ranking"),  # TODO - add ranking
    'title': _("by alphabet"),
    '-created': _("by date"),
}
CATEGORY_PHOTO_OPTIONS = ('all', 'photos')
CATEGORY_ORDER_ATTR = 'category_order_attr'
CATEGORY_PHOTO_ATTR = 'category_photo_attr'

WEEK_DAYS = (
    (1, _("Monday")),
    (2, _("Tuesday")),
    (3, _("Wednesday")),
    (4, _("Thursday")),
    (5, _("Friday")),
    (6, _("Saturday")),
    (7, _("Sunday")),
)

MONTHS = (
    (1, _("January")),
    (2, _("February")),
    (3, _("March")),
    (4, _("April")),
    (5, _("May")),
    (6, _("June")),
    (7, _("July")),
    (8, _("August")),
    (9, _("September")),
    (10, _("October")),
    (11, _("November")),
    (12, _("December")),
)

PHOTO_ORDER_GAP = 5

# get function to be load and get qs as arg to return qs by rating
FUNC_QS_BY_RATING = getattr(settings, 'YUMMY_FUNC_QS_BY_RATING', None)

CACHE_TIMEOUT = 60 * 10
CACHE_TIMEOUT_LONG = 60 * 60 * 1

CACHE_PREFIX = 'yummy:dummy'

_CACHE_FUNCTION = getattr(settings, 'YUMMY_CACHE_OBJECT_FUNC', 'yummy.utils.cache.get_cached_model')
GET_CACHE_FUNCTION = lambda: import_module_member(_CACHE_FUNCTION)
LISTING_PAGINATE_BY = getattr(settings, 'YUMMY_LISTING_PAGINATE_BY', 15)

GET_THUMBNAIL_FUNC = getattr(settings, 'YUMMY_GET_THUMBNAIL_FUNC', None)

DEFAULT_COOKBOOK = _("Favorite recipes")
