from datetime import date
from django.core.exceptions import ObjectDoesNotExist
from django.db import models


class CategoryManager(models.Manager):

    def get_query_set(self):
        return super(CategoryManager, self).get_query_set().select_related('parent', 'photo')


class RecipeManager(models.Manager):

    def approved(self):
        return self.get_query_set().filter(is_approved=True)

    def get_query_set(self):
        return super(RecipeManager, self).get_query_set().select_related()


class RecipeRecommendationManager(models.Manager):

    def get_actual(self):
        today = date.today()
        return self.get_query_set().filter(
            (models.Q(day_to__gte=today) | models.Q(day_to__isnull=True)),
            day_from__lte=today, recipe__is_approved=True
        ).select_related('recipe')



class WeekMenuManager(models.Manager):

    def get_actual(self):
        today = date.today()
        weekday =  date.isoweekday(today)
        foo, week_no, foo = date.isocalendar(today)
        try:
            return self.get_query_set().select_related('soup', 'meal', 'dessert').get(day=weekday, even_week=bool((week_no+1)%2))
        except ObjectDoesNotExist:
            pass
