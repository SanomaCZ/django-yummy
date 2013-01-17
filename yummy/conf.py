from django.conf import settings
from django.utils.translation import npgettext_lazy, ugettext_lazy as _

from yummy.utils import import_module_member


UNITS = (
    (0, lambda c=1: npgettext_lazy('unit', 'piece', 'pieces', c), lambda c=1: npgettext_lazy('unit', 'pc', 'pcs', c)),
    (1, lambda c=1: npgettext_lazy('unit', 'gram', 'grams', c), 'g'),
    (2, lambda c=1: npgettext_lazy('unit', 'dekagram', 'dekagrams', c), 'dkg'),
    (3, lambda c=1: npgettext_lazy('unit', 'kilogram', 'kilograms', c), 'kg'),
    (4, lambda c=1: npgettext_lazy('unit', 'mililiter', 'mililiters', c), 'ml'),
    (5, lambda c=1: npgettext_lazy('unit', 'deciliter', 'deciliters', c), 'dl'),
    (6, lambda c=1: npgettext_lazy('unit', 'liter', 'liters', c), 'l'),
    (7, lambda c=1: npgettext_lazy('unit', 'packaging', 'packagings', c), 'pack'), #baleni
    (8, lambda c=1: npgettext_lazy('unit', 'package', 'packages', c), 'pkg'), #balicek
    (9, lambda c=1: npgettext_lazy('unit', 'part', 'parts', c), 'bit'), #dilek
    (10, lambda c=1: npgettext_lazy('unit', 'cup', 'cups', c)), #hrnek
    (11, lambda c=1: npgettext_lazy('unit', 'handful', 'handful', c)), #hrst
    (12, lambda c=1: npgettext_lazy('unit', 'drop', 'drops', c)), #kapka
    (13, lambda c=1: npgettext_lazy('unit', 'crubicle', 'crubicles', c)), #kelimek
    (14, lambda c=1: npgettext_lazy('unit', 'can', 'cans', c)), #plechovka
    (15, lambda c=1: npgettext_lazy('unit', 'scoop', 'scoops', c)), #kopecek
    (16, lambda c=1: npgettext_lazy('unit', 'cube', 'cubes', c)), #kostka
    (17, lambda c=1: npgettext_lazy('unit', 'ball', 'balls', c)), #kulicka
    (18, lambda c=1: npgettext_lazy('unit', 'bottle', 'bottles', c)), #lahev
    (19, lambda c=1: npgettext_lazy('unit', 'spoon', 'spoons', c)), #lzice
    (20, lambda c=1: npgettext_lazy('unit', 'teaspoon', 'teaspoons', c)), #lzicka
    (21, lambda c=1: npgettext_lazy('unit', 'bowl', 'bowls', c)), #miska
    (22, lambda c=1: npgettext_lazy('unit', 'bud', 'buds', c)), #palicka
    (23, lambda c=1: npgettext_lazy('unit', 'slice', 'slices', c)), #platek
    (24, lambda c=1: npgettext_lazy('unit', 'tin', 'tins', c)), #konzerva
    (25, lambda c=1: npgettext_lazy('unit', 'jar', 'jars', c)), #sklenice
    (26, lambda c=1: npgettext_lazy('unit', 'sprig', 'sprigs', c)), #snitka
    (27, lambda c=1: npgettext_lazy('unit', 'clove', 'cloves', c)), #strouzek
    (28, lambda c=1: npgettext_lazy('unit', 'bunch', 'bunches', c)), #svazek
    (29, lambda c=1: npgettext_lazy('unit', 'crumb', 'crumbs', c)), #spetka
    (30, lambda c=1: npgettext_lazy('unit', 'teacup', 'teacups', c)), #salek
    (31, lambda c=1: npgettext_lazy('unit', 'twig', 'twigs', c)), #vetvicka
    (32, lambda c=1: npgettext_lazy('unit', 'serving', 'servings', c)), #porce
    (33, lambda c=1: npgettext_lazy('unit', 'leaf', 'leaves', c)), #list
    (34, lambda c=1: npgettext_lazy('unit', 'microphyll', 'microphylles', c)), #listek, small leaf
    (35, lambda c=1: npgettext_lazy('unit', 'batch', 'batches', c)), #davka
)

UNIT_CHOICES = tuple((unit[0], unit[1]()) for unit in UNITS)
DICT_UNITS = dict(tuple(unit[:2] for unit in UNITS))


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
