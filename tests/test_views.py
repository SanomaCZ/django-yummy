from django.contrib.auth.models import User, AnonymousUser
from django.contrib.messages.storage.base import BaseStorage
from django.contrib.sessions.backends.file import SessionStore
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.http import HttpRequest
from django.test import TestCase

from nose import tools

from yummy import conf
from yummy.models import Category, Cuisine, Recipe, Ingredient, IngredientGroup, CookBook
from yummy.views import FavoriteRecipeAdd


def init_request():
    request = HttpRequest()
    request.method = 'GET'
    request.session = SessionStore()
    request.session.create()
    request._messages = BaseStorage(request)
    request.user = AnonymousUser()

    return request


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
        self.client.get(self.recipe.get_absolute_url())

        self.client.get(reverse('yummy:ingredient_index'))
        self.client.get(reverse('yummy:ingredient_group', args=(self.ingroup.slug,)))
        self.client.get(reverse('yummy:ingredient_detail', args=(self.ingredient.slug,)))
        self.client.get(self.ingredient.get_absolute_url())

        self.client.get(reverse('yummy:menu_load_data'))

        self.client.get(reverse('yummy:authors_list'))
        self.client.get(reverse('yummy:author_recipes', args=(self.user.pk,)))


class TestCookBookViews(TestCase):


    def setUp(self):
        cache.clear()

        self.user = User.objects.create(username='user')

        self.cat = Category.objects.create(
            title="foo",
            path='foo'
        )

        self.recipe = Recipe.objects.create(
            title='foo',
            category=self.cat,
            preparation_time=10,
            owner=self.user
        )

        self.request = init_request()
        self.request.user = self.user

    def test_create_default_cookbook_in_add_form(self):

        tools.assert_equals(0, CookBook.objects.filter(owner=self.user).count())

        view = FavoriteRecipeAdd.as_view()
        view(self.request, recipe_id=self.recipe.pk)

        tools.assert_equals(1, CookBook.objects.filter(owner=self.user).count())
