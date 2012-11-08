from django.conf import settings
from django.utils.translation import npgettext, ugettext_lazy as _
from yummy.utils import import_module_member

UNITS = (
    (0, npgettext('unit', 'piece', 'pieces', 1), npgettext('unit', 'pc', 'pcs', 1)),
    (1, npgettext('unit', 'gram', 'grams', 1), 'g'),
    (2, npgettext('unit', 'dekagram', 'dekagrams', 1), 'dkg'),
    (3, npgettext('unit', 'kilogram', 'kilograms', 1), 'kg'),
    (4, npgettext('unit', 'mililiter', 'mililiters', 1), 'ml'),
    (5, npgettext('unit', 'deciliter', 'deciliters', 1), 'dl'),
    (6, npgettext('unit', 'liter', 'liters', 1), 'l'),
    (7, npgettext('unit', 'packaging', 'packagings', 1), 'pack'), #baleni
    (8, npgettext('unit', 'package', 'packages', 1), 'pkg'), #balicek
    (9, npgettext('unit', 'part', 'parts', 1), 'bit'), #dilek
    (10, npgettext('unit', 'cup', 'cups', 1)), #hrnek
    (11, npgettext('unit', 'handful', 'handful', 1)), #hrst
    (12, npgettext('unit', 'drop', 'drops', 1)), #kapka
    (13, npgettext('unit', 'crubicle', 'crubicles', 1)), #kelimek
    (14, npgettext('unit', 'can', 'cans', 1)), #plechovka
    (15, npgettext('unit', 'scoop', 'scoops', 1)), #kopecek
    (16, npgettext('unit', 'cube', 'cubes', 1)), #kostka
    (17, npgettext('unit', 'ball', 'balls', 1)), #kulicka
    (18, npgettext('unit', 'bottle', 'bottles', 1)), #lahev
    (19, npgettext('unit', 'spoon', 'spoons', 1)), #lzice
    (20, npgettext('unit', 'teaspoon', 'teaspoons', 1)), #lzicka
    (21, npgettext('unit', 'bowl', 'bowls', 1)), #miska
    (22, npgettext('unit', 'bud', 'buds', 1)), #palicka
    (23, npgettext('unit', 'slice', 'slices', 1)), #platek
    (24, npgettext('unit', 'tin', 'tins', 1)), #konzerva
    (25, npgettext('unit', 'jar', 'jars', 1)), #sklenice
    (26, npgettext('unit', 'sprig', 'sprigs', 1)), #snitka
    (27, npgettext('unit', 'clove', 'cloves', 1)), #strouzek
    (28, npgettext('unit', 'bunch', 'bunches', 1)), #svazek
    (29, npgettext('unit', 'crumb', 'crumbs', 1)), #spetka
    (30, npgettext('unit', 'teacup', 'teacups', 1)), #salek
    (31, npgettext('unit', 'twig', 'twigs', 1)), #vetvicka
    (32, npgettext('unit', 'serving', 'servings', 1)), #porce
    (33, npgettext('unit', 'leaf', 'leaves', 1)), #list
    (34, npgettext('unit', 'microphyll', 'microphylles', 1)), #listek, small leaf
    (35, npgettext('unit', 'batch', 'batches', 1)), #davka
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

CACHE_PREFIX = 'yummy:dummy'

_CACHE_FUNCTION = getattr(settings, 'YUMMY_CACHE_OBJECT_FUNC', 'yummy.utils.cache.get_cached_model')
GET_CACHE_FUNCTION = lambda: import_module_member(_CACHE_FUNCTION)
LISTING_PAGINATE_BY = getattr(settings, 'YUMMY_LISTING_PAGINATE_BY', 15)
