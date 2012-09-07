from django.utils.translation import ngettext, npgettext, ugettext_lazy as _

#ngettext(singular, plural, number)
#npgettext(context, singular, plural, number)

UNIT_CHOICES = (
    (0, npgettext('unit', 'cup', 'cups', 0)),
)

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
