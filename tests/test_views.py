from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.test import TestCase
from yummy import conf

from yummy.models import Category, Cuisine, Recipe, Ingredient, IngredientGroup


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

        self.ingredient = Ingredient.objects.create(
            name='ingredient',
            default_unit=conf.UNIT_CHOICES[0][0]
        )

        self.ingroup = IngredientGroup.objects.create(
            name='ingroup'
        )


    def test_basic_views(self):
        self.client.get(reverse('yummy:category_index'))

        self.client.get(reverse('yummy:category_detail', args=(self.cat.path,)))

        self.client.get(reverse('yummy:category_reorder', args=('foo', )))

        self.client.get(reverse('yummy:cuisine_detail', args=(self.cuisine.slug, )))

        self.client.get(reverse('yummy:recipe_detail', args=(self.recipe.category.path, self.recipe.slug, self.recipe.pk)))

        self.client.get(reverse('yummy:ingredient_index'))

        self.client.get(reverse('yummy:ingredient_group', args=(self.ingroup.slug,)))

        self.client.get(reverse('yummy:ingredient_detail', args=(self.ingredient.slug,)))

        self.client.get(reverse('yummy:author_recipes', args=(self.user.pk,)))

