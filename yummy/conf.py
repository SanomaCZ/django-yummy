from django.conf import settings
from django.utils.translation import npgettext, ugettext_lazy as _

UNITS = (
    (0, npgettext('unit', 'piece', 'pieces', 1), npgettext('unit', 'pc', 'pcs', 1)),
    (1, npgettext('unit', 'gram', 'grams', 1), 'g'),
    (2, npgettext('unit', 'dekagram', 'dekagrams', 1), 'dkg'),
    (3, npgettext('unit', 'kilogram', 'kilograms', 1), 'kg'),
    (4, npgettext('unit', 'mililiter', 'mililiters', 1), 'ml'),
    (5, npgettext('unit', 'deciliter', 'deciliters', 1), 'dl'),
    (6, npgettext('unit', 'liter', 'liters', 1), 'l'),
    (100, npgettext('unit', 'cup', 'cups', 1), npgettext('unit', 'cup', 'cups', 1)),
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
