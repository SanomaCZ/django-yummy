from datetime import date
from django import template

from yummy.models import RecipeRecommendation, WeekMenu, Category
from yummy import conf

register = template.Library()


class RecommendationNode(template.Node):
    def __init__(self, count, varname):
        self.count, self.varname = count, varname

    def render(self, context):
        qs = RecipeRecommendation.objects.get_actual()
        context[self.varname] = tuple(one.recipe for one in qs[:self.count])
        return ''


@register.tag
def yummy_recipe_recommendation(parser, token):
    """
    Get N of recommended recipe for current date. If N is not set, default is used.

    syntax::

        {% yummy_recipe_recommendation [<count>] as <var> %}

    examples::

        {% yummy_recipe_recommendation as recommended_recipes  %}
        {% yummy_recipe_recommendation 5 as recommended_recipes %}

    """

    bits = token.split_contents()

    if len(bits) not in (3, 4) or bits[-2] != 'as':
        raise template.TemplateSyntaxError('Usage: {% yummy_recipe_recommendation [<count>] as <variable> %}')

    varname = bits[-1]
    count = conf.RECIPE_RECOMMENDATIONS_COUNT if len(bits) == 3 else bits[1]

    return RecommendationNode(count, varname)


@register.inclusion_tag("yummy/day_menu.html")
def yummy_day_menu():
    """
    renders daily menu with given template

    example:
        {% yummy_day_menu %}

    :return: context data for inclusion tag decorator
    :rtype: dict
    """
    menu = WeekMenu.objects.get_actual()

    current_day = date.isoweekday(date.today())
    return {
        'current_week_day': current_day,
        'current_menu': menu.get(current_day) or {},
        'week_days': conf.WEEK_DAYS,
    }


class CategoriesNode(template.Node):

    def __init__(self, category, varname):
        self.category, self.varname = category, varname

    def render(self, context):
        if self.category is not None:
            c = template.Variable(self.category).resolve(context)
            qs = Category.objects.filter(parent=c)
        else:
            qs = Category.objects.filter(parent__isnull=True)

        context[self.varname] = list(qs)
        return ''


@register.tag
def yummy_get_categories(parser, token):
    """
    Returns category children if category variable is defined, or root categories.

    syntax::

        {% yummy_get_categories [from <category>] as <var> %}

    examples::

        {% yummy_get_categories as categories  %}
        {% yummy_get_categories from category as recommended_recipes %}

    """

    bits = token.split_contents()

    if len(bits) not in (3, 5) or bits[-2] != 'as':
        raise template.TemplateSyntaxError('Usage: {% yummy_get_categories [from <category>] as <variable> %}')

    varname = bits[-1]
    category = None if len(bits) == 3 else bits[2]

    return CategoriesNode(category, varname)
