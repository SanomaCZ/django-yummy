from datetime import date
from django.core.cache import cache
from django.db import models

from yummy import conf


class CookBookManager(models.Manager):

    def create_default(self, user):
        return self.get_query_set().get_or_create(owner=user, title=unicode(conf.DEFAULT_COOKBOOK))


class RecipePhotoManager(models.Manager):

    def visible(self):
        return self.get_query_set().filter(is_visible=True)


class CategoryManager(models.Manager):

    def get_query_set(self):
        return super(CategoryManager, self).get_query_set().select_related('parent', 'photo')


class RecipeManager(models.Manager):

    def public(self):
        return self.approved().filter(is_public=True)

    def approved(self):
        return self.get_query_set().filter(is_approved=True)

    def checked(self):
        return self.public().filter(is_checked=True)

    def get_query_set(self):
        return super(RecipeManager, self).get_query_set().select_related()


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
        return self.get_query_set().filter(
            (models.Q(day_to__gte=today) | models.Q(day_to__isnull=True)),
            day_from__lte=today, recipe__is_approved=True, recipe__is_public=True,
        ).select_related('recipe').order_by('-day_from')


class WeekMenuManager(models.Manager):

    def get_actual(self):
        week_no = date.isocalendar(date.today())[1]
        is_even_week = bool((week_no + 1) % 2)

        items = self.get_query_set().\
                    select_related('soup', 'meal', 'dessert').\
                    filter(even_week=is_even_week)

        return dict( [(one.day, one) for one in items ] )


class IngredientManager(models.Manager):

    def approved(self):
        return self.get_query_set().filter(is_approved=True)


    def get_names_list(self, recache=False):
        cache_key = 'ingredient_get_names_list'
        ingredients = cache.get(cache_key)
        if ingredients is None or recache:
            ingredients = self.approved().values_list('name', flat=True)
            cache.set(cache_key, ingredients)
        return ingredients
