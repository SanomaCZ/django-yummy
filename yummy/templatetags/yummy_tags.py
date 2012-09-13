from django import template

from yummy.models import RecipeRecommendation, WeekMenu
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

    if (len(bits) == 3 and bits[1] != 'as') or (len(bits) == 4 and bits[2] != 'as'):
        raise template.TemplateSyntaxError('Usage: {% yummy_recipe_recommendation [<count>] as <variable> %}')

    if len(bits) == 3:
        count, varname = conf.RECIPE_RECOMMENDATIONS_COUNT, bits[2]
    else:
        count, varname = bits[1], bits[3]

    return RecommendationNode(count, varname)



class DayMenuNode(template.Node):
    def __init__(self, varname):
        self.varname = varname

    def render(self, context):
        context[self.varname] = WeekMenu.objects.get_actual()
        return ''


@register.tag
def yummy_day_menu(parser, token):
    """
    Get daily menu for current weekday in odd/even weeek

    syntax:
        {% yummy_day_menu as <var> %}

    examples:

        {% yummy_day_menu as menu %}

        {{ menu.soup }} - {{ menu.meal }} - {{ menu.dessert }}
    """
    bits = token.split_contents()

    if len(bits) != 3 or bits[1] != 'as':
        raise template.TemplateSyntaxError('Usage: {% yummy_day_menu as <variable> %}')

    foo, foo, varname = bits
    return DayMenuNode(varname)
