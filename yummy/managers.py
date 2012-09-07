from django.db import models


class CategoryManager(models.Manager):

    def get_query_set(self):
        return super(CategoryManager, self).get_query_set().select_related('parent', 'photo')


class RecipeManager(models.Manager):

    def approved(self):
        return self.get_query_set().filter(is_approved=True)

    def get_query_set(self):
        return super(RecipeManager, self).get_query_set().select_related()
