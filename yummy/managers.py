from datetime import date
from django.core.cache import cache
from django.db import models

from yummy.utils import get_model
from yummy import conf


class CookBookManager(models.Manager):

    def create_default(self, user):
        return self.get_or_create(owner=user, is_default=True, defaults={
            'title': unicode(conf.DEFAULT_COOKBOOK)
        })

    def get_user_recipes_count(self, owner, recache=False):
        cache_key = "%s_get_all_cookbooks_recipes" % owner.pk
        recipes_count = cache.get(cache_key)
        if recipes_count is None or recache:
            from yummy.models import CookBookRecipe
            recipes_count = CookBookRecipe.objects.filter(cookbook__owner=owner).count()
            cache.set(cache_key, recipes_count)
        return recipes_count

    def get_user_cookbook_items_for_recipe(self, owner, recipe, recache=False):
        recipe_id = isinstance(recipe, get_model('yummy', 'recipe')) and recipe.pk or recipe
        cache_key = "recipe_%s_cbowner_%s_get_cookbook_items" % (recipe_id, owner.pk)
        items = cache.get(cache_key)
        if items is None or recache:
            from yummy.models import CookBookRecipe
            items = CookBookRecipe.objects.filter(cookbook__owner=owner, recipe__pk=recipe_id)
            cache.set(cache_key, list(items))
        return items


class RecipePhotoManager(models.Manager):

    def visible(self):
        return self.filter(is_visible=True)


class CategoryManager(models.Manager):

    def get_queryset(self):
        parent = super(CategoryManager, self)
        queryset_method = hasattr(parent, 'get_queryset') and getattr(parent, 'get_queryset') or getattr(parent, 'get_query_set')
        return queryset_method().select_related('parent', 'photo')

    # backward compatibility
    get_query_set = get_queryset


class RecipeManager(models.Manager):

    def public(self):
        return self.approved().filter(is_public=True)

    def approved(self):
        return self.filter(is_approved=True)

    def checked(self):
        return self.public().filter(is_checked=True)

    def get_queryset(self):
        parent = super(RecipeManager, self)
        queryset_method = hasattr(parent, 'get_queryset') and getattr(parent, 'get_queryset') or getattr(parent, 'get_query_set')
        return queryset_method().select_related()

    # backward compatibility
    get_query_set = get_queryset


class RecipeRecommendationManager(models.Manager):

    def get_actual(self):
        """
        if there is more valid records for current date, order them by day_from
        (in example lower, r3 has highest priority)

              today
                |
        r1  ----+-
                |
        r2    --+---
                |
        r3     -+----
        """
        today = date.today()
        return self.filter(
            (models.Q(day_to__gte=today) | models.Q(day_to__isnull=True)),
            day_from__lte=today, recipe__is_approved=True, recipe__is_public=True,
        ).select_related('recipe').order_by('-day_from')


class WeekMenuManager(models.Manager):

    def get_actual(self):
        week_no = date.isocalendar(date.today())[1]
        is_even_week = bool((week_no + 1) % 2)

        items = self.select_related('soup', 'meal', 'dessert').\
            filter(even_week=is_even_week)

        return dict([(one.day, one) for one in items])


class IngredientManager(models.Manager):

    def approved(self):
        return self.filter(is_approved=True)

    def get_names_list(self, recache=False):
        cache_key = 'ingredient_get_names_list'
        ingredients = cache.get(cache_key)
        if ingredients is None or recache:
            ingredients = self.approved().values_list('name', flat=True)
            cache.set(cache_key, ingredients)
        return ingredients
