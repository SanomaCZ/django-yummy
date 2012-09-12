from django import template

from yummy.models import RecipeRecommendation
from yummy import conf

register = template.Library()


class RecommendationNode(template.Node):
    def __init__(self, count, varname):
        self.count, self.varname = count, varname

    def render(self, context):
            qs = RecipeRecommendation.objects.get_actual()
            context[self.varname] = [one.recipe for one in qs[:self.count]]
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
