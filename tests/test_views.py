from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.test import TestCase

from yummy.models import Category, Cuisine, Recipe


class TestViews(TestCase):

    def setUp(self):
        cache.clear()

        self.cat = Category.objects.create(
            title="foo",
            path='foo'
            )

        self.cuisine = Cuisine.objects.create(name='ceska')

        self.user = User.objects.create(username='user')

        self.recipe = Recipe.objects.create(
            title='foo',
            category=self.cat,
            preparation_time=10,
            owner=self.user
        )

    def test_basic_views(self):
        self.client.get(reverse('category_index'))

        self.client.get(reverse('category_detail', args=(self.cat.path,)))

        self.client.get(reverse('category_reorder', args=('foo', )))

        self.client.get(reverse('cuisine_detail', args=(self.cuisine.slug, )))

        self.client.get(reverse('recipe_detail', args=(self.recipe.category.path, self.recipe.slug, self.recipe.pk)))
