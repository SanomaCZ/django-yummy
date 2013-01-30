from datetime import date
from django import template
from django.core.cache import cache

from yummy.models import RecipeRecommendation, WeekMenu, Category, CookBookRecipe, CookBook
from yummy import conf

register = template.Library()


class RecommendationNode(template.Node):
    def __init__(self, count, varname):
        self.count, self.varname = count, varname

    def _get_recommendations(self):
        key = 'reciperecommendations:%d' % self.count
        r = cache.get(key)
        if r is None:
            qs = RecipeRecommendation.objects.get_actual()
            r = tuple(one.recipe for one in qs[:self.count])
            cache.set(key, r, conf.CACHE_TIMEOUT)
        return r

    def render(self, context):
        context[self.varname] = self._get_recommendations()
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
    count = conf.RECIPE_RECOMMENDATIONS_COUNT if len(bits) == 3 else int(bits[1])

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
    current_day = date.isoweekday(date.today())
    key = 'yummy_day_menus:%s' % current_day
    menu = cache.get(key)
    if menu is None:
        menu = WeekMenu.objects.get_actual()
        cache.set(key, menu, conf.CACHE_TIMEOUT_LONG)

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
            pk = c.pk
        else:
            qs = Category.objects.filter(parent__isnull=True)
            pk = 0

        key = 'yummy_get_categories:%d' % pk
        c = cache.get(key)
        if c is None:
            c = list(qs)
            cache.set(key, c, conf.CACHE_TIMEOUT_LONG)

        context[self.varname] = c
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


@register.filter
def in_cookbook(recipe, owner):
    return bool(CookBookRecipe.objects.filter(recipe=recipe, cookbook__owner=owner).count())


@register.simple_tag
def cookbook_recipes_count(user):
    """
    return count of user's favorite recipes

    syntax::

        {% cookbook_recipes_count owner %}
    """
    count = CookBook.objects.get_user_recipes_count(owner=user)
    return count


class UserCookbookItemsNode(template.Node):
    def __init__(self, owner, recipe, count, varname):
        self.owner, self.recipe = owner, recipe
        self.count, self.varname = count, varname

    def render(self, context):
        owner = template.Variable(self.owner).resolve(context)
        recipe = template.Variable(self.recipe).resolve(context)
        items = CookBook.objects.get_user_cookbook_items_for_recipe(owner=owner, recipe=recipe)
        if self.count == 1:
            try:
                item = items[0]
            except IndexError:
                item = None
            context[self.varname] = item
            return ''
        elif self.count:
            items = items[:self.count]
        context[self.varname] = items
        return ''


@register.tag
def yummy_user_cookbook_items(parser, token):
    """
    Get N or all of user's cookbook items for given recipe

    syntax::

        {% yummy_user_cookbook_items owner recipe [<count>] as <var> %}

    examples::

        {% yummy_user_cookbook_items user recipe as user_cookbook_items  %}
        {% yummy_user_cookbook_items user recipe 5 as user_cookbook_items %}

    """

    bits = token.split_contents()

    if len(bits) not in (5, 6) or bits[-2] != 'as':
        raise template.TemplateSyntaxError('Usage: {% yummy_user_cookbook_items owner recipe [<count>] as <variable> %}')

    varname = bits[-1]
    owner = bits[1]
    recipe = bits[2]
    count = None if len(bits) == 5 else int(bits[3])

    return UserCookbookItemsNode(owner, recipe, count, varname)
