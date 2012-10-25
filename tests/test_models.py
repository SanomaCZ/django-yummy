# -*- coding: utf-8 -*-
from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django import VERSION as DJANGO_VERSION
from mock import patch

from nose import tools, SkipTest
from yummy import conf

from yummy.models import ( Category, Recipe, RecipeRecommendation, CookingType,
    Cuisine, WeekMenu, IngredientGroup, Ingredient, Photo, RecipePhoto)


class MockedDate(date):
    pass


def create_recipe(**kwargs):
    """
    :return: recipe
    :rtype: Recipe
    """
    params = dict(
        title='generic recipe',
        preparation_time=20,
        is_approved=True
    )
    params.update(kwargs)
    return Recipe.objects.create(**params)


class TestRecipeRecommendationModel(TestCase):

    def setUp(self):
        super(TestRecipeRecommendationModel, self).setUp()
        cache.clear()

        self.user = User.objects.create_user(username='foo')
        self.cat = Category.objects.create(title="generic cat")
        self.recipe = create_recipe(owner=self.user, category=self.cat)

    def test_invalid_date_range_save_raises_validation_error(self):
        today = date.today()
        tools.assert_raises(IntegrityError, lambda: RecipeRecommendation.objects.create(
            recipe=self.recipe,
            day_from=today,
            day_to=today-timedelta(days=1)
            ))

    def test_valid_date_range_save_pass(self):
        today = date.today()
        record = RecipeRecommendation.objects.create(recipe=self.recipe,
                    day_from=today, day_to=today + timedelta(days=1))
        tools.assert_not_equals(record.pk, None)

    def test_empty_ending_date_save_pass(self):
        today = date.today()
        record = RecipeRecommendation.objects.create(recipe=self.recipe, day_from=today)
        tools.assert_equals(record.day_to, None)

    def test_unapproved_recipe_save_raises(self):
        today = date.today()

        self.recipe.is_approved = False
        self.recipe.save()

        tools.assert_raises(IntegrityError, lambda: RecipeRecommendation.objects.create(
            recipe=self.recipe, day_from=today)
        )

    def test_date_invalid_chronology_borders_raises(self):
        today = date.today()
        tools.assert_raises(IntegrityError, lambda: RecipeRecommendation.objects.create(
            recipe=self.recipe,
            day_to=today - timedelta(days=2),
            day_from=today - timedelta(days=1)
        ))

    def test_recommendation_manager_get_actual_ignores_past_records(self):
        today = date.today()
        RecipeRecommendation.objects.create(
            recipe=self.recipe,
            day_from=today-timedelta(days=2),
            day_to=today-timedelta(days=1),
        )

        tools.assert_equals([], list(RecipeRecommendation.objects.get_actual()))

    def test_recommendation_manager_get_actual_priorized_by_start_date(self):
        today = date.today()

        r1 = RecipeRecommendation.objects.create(
            recipe=self.recipe,
            day_from=today - timedelta(days=2),
            day_to=today + timedelta(days=1),
        )

        r2 = RecipeRecommendation.objects.create(
            recipe=self.recipe,
            day_from=today - timedelta(days=1),
            day_to=today + timedelta(days=1),
        )

        tools.assert_equals(r2, RecipeRecommendation.objects.get_actual()[0])



class TestCategoryModel(TestCase):

    def setUp(self):
        super(TestCategoryModel, self).setUp()
        cache.clear()

        self.c0 = Category.objects.create(title=u"Ámen", slug="amen")
        self.c1 = Category.objects.create(parent=self.c0, title=u"Mňam mňam", slug="mnam-mnam")

    def tearDown(self):
        super(TestCategoryModel, self).tearDown()
        Category.objects.all().delete()

    def test_nested_category_path(self):
        tools.assert_equal('amen', self.c0.path)
        tools.assert_equal('amen/mnam-mnam', self.c1.path)

    def test_clean_parent_category_raise_validation(self):
        self.c0.parent = self.c0
        tools.assert_raises(ValidationError, self.c0.clean)

    def test_save_parent_category_raise_integrity(self):
        self.c0.parent = self.c0
        tools.assert_raises(IntegrityError, self.c0.save)

    def test_recursion_save(self):
        self.c0.parent = self.c1
        tools.assert_raises(IntegrityError, self.c0.save)

    def test_recursion_clean(self):
        self.c0.parent = self.c1
        tools.assert_raises(ValidationError, self.c0.clean)

    def test_path_is_unique_on_clean_not_only_on_save(self):
        new_c = Category(parent=self.c0, title="Mňam mňam", slug="mnam-mnam")
        tools.assert_raises(ValidationError, new_c.clean)

    def test_path_is_unique_on_clean_no_parent(self):
        new_c = Category(title="Ámen", slug="amen")
        tools.assert_raises(ValidationError, new_c.clean)

    def test_path_is_unique(self):
        new_c_ok = Category(title="Ámen 2", slug="amen-2")
        new_c_no = Category(title="Ámen", slug="amen")
        tools.assert_true(new_c_ok.path_is_unique())
        tools.assert_false(new_c_no.path_is_unique())

    def test_path_changed_correctly(self):
        c01 = Category.objects.create(title="Jajky", slug="jajky")
        c12 = Category.objects.create(parent=self.c1, title="Mňam mňam", slug="mnam-mnam-2")
        self.c1.parent = c01
        self.c1.save()
        cx = Category.objects.get(slug="mnam-mnam-2")

        tools.assert_equal('jajky/mnam-mnam/mnam-mnam-2', cx.path)

    def test_category_level(self):
        tools.assert_equal(1, self.c0.level)
        tools.assert_equal(2, self.c1.level)

    def test_get_children(self):
        c01 = Category.objects.create(title="Jajky", slug="jajky")
        c12 = Category.objects.create(parent=self.c1, title="Mňam mňam", slug="mnam-mnam-2")

        tools.assert_equal(self.c1, self.c0.get_children()[0])
        tools.assert_equal(c12, self.c1.get_children()[0])

    def test_get_descendants(self):
        c12 = Category.objects.create(parent=self.c1, title="Mňam mňam", slug="mnam-mnam-2")

        tools.assert_true(self.c1 in self.c0.get_descendants())
        tools.assert_true(c12 in self.c0.get_descendants())

    def test_is_ancestor_if_category_none(self):
        tools.assert_false(self.c0.is_ancestor_of())

    def test_is_ancestor(self):
        tools.assert_false(self.c1.is_ancestor_of(self.c0))
        tools.assert_true(self.c0.is_ancestor_of(self.c1))

    def test_unicode_returns_title(self):
        tools.assert_equal(u"Mňam mňam", "%s" % self.c1.__unicode__())

    def test_get_chained_title(self):
        c2 =  Category.objects.create(parent=self.c1, title=u"Kůň", slug="kun")
        tools.assert_equal(u"Ámen / Mňam mňam / Kůň", "%s" % c2.chained_title)

    def test_select_related(self):
        if DJANGO_VERSION[:2] < (1, 4):
            raise SkipTest()
        self.assertNumQueries(1, lambda: Category.objects.get(slug="mnam-mnam").parent.slug)

    def test_get_absolute_url(self):
        tools.assert_equal('/category/amen/', self.c0.get_absolute_url())
        tools.assert_equal('/category/amen/mnam-mnam/', self.c1.get_absolute_url())


class TestRecipeModel(TestCase):

    def setUp(self):
        super(TestRecipeModel, self).setUp()
        cache.clear()

        self.user = User.objects.create_user(username='foo')
        self.cat = Category.objects.create(title="generic cat")

    def test_objects_get_approved_returns_empty(self):
        recipe = create_recipe(is_approved=False, owner=self.user, category=self.cat)

        tools.assert_equals([], list(Recipe.objects.approved()))
        tools.assert_equals([recipe], list(Recipe.objects.all()))

    def test_objects_get_approved_returns_approved(self):
        recipe = create_recipe(owner=self.user, category=self.cat)

        tools.assert_equals([recipe], list(Recipe.objects.approved()))
        tools.assert_equals([recipe], list(Recipe.objects.all()))

    def test_unicode_pass(self):
        #coverage ftw!
        title = u'sytý nášup'
        recipe = create_recipe(owner=self.user, category=self.cat, title=title)
        tools.assert_equals(True, title in unicode(recipe))

    def test_reoder_owner_photo(self):

        nonowner = User.objects.create_user(username='nonauthor')

        nonowner_photo = Photo.objects.create(width=1, height=1, owner=nonowner)
        owner_photo = Photo.objects.create(width=1, height=1, owner=self.user)

        recipe = create_recipe(owner=self.user, category=self.cat)

        RecipePhoto.objects.create(recipe=recipe, photo=nonowner_photo, order=1)
        owner_recipe_photo = RecipePhoto.objects.create(recipe=recipe, photo=owner_photo, order=2)

        top_photo = recipe.get_top_photo()

        tools.assert_equals(top_photo.pk, owner_recipe_photo.pk)


class TestCookingTypeModel(TestCase):

    def setUp(self):
        super(TestCookingTypeModel, self).setUp()
        cache.clear()

    def test_unique_slug_violation_raises(self):
        cook_type = CookingType.objects.create(name='foobar')

        tools.assert_raises(IntegrityError, lambda: CookingType.objects.create(name='foobar'))

    def test_unicode_pass(self):
        name=u'vegetariánská díákrítíká'
        cook_type = CookingType.objects.create(name=name)

        tools.assert_equals(True, name in unicode(cook_type))

class TestCuisineModel(TestCase):

    def setUp(self):
        super(TestCuisineModel, self).setUp()
        cache.clear()

    def test_unique_slug_violation_raises(self):
        Cuisine.objects.create(name='foobar')

        tools.assert_raises(IntegrityError, lambda: Cuisine.objects.create(name='foobar'))

    def test_unicode_pass(self):
        name=u'árménská kúchýně'
        cook_type = Cuisine.objects.create(name=name)
        tools.assert_equals(True, name in unicode(cook_type))


class TestIngredientGroupModel(TestCase):

    def setUp(self):
        super(TestIngredientGroupModel, self).setUp()
        cache.clear()

    def test_unique_slug_violation_raises(self):
        IngredientGroup.objects.create(name='foobar')

        tools.assert_raises(IntegrityError, lambda: IngredientGroup.objects.create(name='foobar'))

    def test_unicode_pass(self):
        name=u'árménská'
        group = IngredientGroup.objects.create(name=name)
        tools.assert_equals(True, name in unicode(group))


class TestIngredientModel(TestCase):

    def setUp(self):
        super(TestIngredientModel, self).setUp()
        cache.clear()

    def test_unique_slug_violation_raises(self):
        Ingredient.objects.create(name='foobar', default_unit=conf.UNITS[0][0])

        tools.assert_raises(IntegrityError,
                            lambda: Ingredient.objects.create(
                                name='foobar',
                                default_unit=conf.UNITS[0][0]))

    def test_unicode_pass(self):
        name=u'čokoláda'
        ingredient = Ingredient.objects.create(name=name, default_unit=conf.UNITS[0][0])
        tools.assert_equals(True, name in unicode(ingredient))


class TestWeekMenuModel(TestCase):

    def setUp(self):
        super(TestWeekMenuModel, self).setUp()
        cache.clear()

    def test_day_week_combinations_violation_raises(self):
        menu_item = WeekMenu.objects.create(day=conf.WEEK_DAYS[0][0], even_week=False)

        tools.assert_not_equals(None, menu_item.pk)
        tools.assert_raises(IntegrityError, lambda: WeekMenu.objects.create(
                                                    day=conf.WEEK_DAYS[0][0],
                                                    even_week=False))

    def test_day_even_odd_week_combinations_pass(self):
        menu_item = WeekMenu.objects.create(day=conf.WEEK_DAYS[0][0], even_week=False)
        next_item = WeekMenu.objects.create(day=conf.WEEK_DAYS[0][0], even_week=True)

        tools.assert_not_equals(menu_item, next_item)

    @patch('yummy.managers.date', MockedDate)
    def test_objects_get_actual_returns_valid_item(self):
        #monday odd week
        actual_item = WeekMenu.objects.create(day=1, even_week=False)

        #monday, odd week
        MockedDate.today = classmethod(lambda cls: date(2012, 1, 2))

        obtained_item = WeekMenu.objects.get_actual()

        tools.assert_equals({1: actual_item}, obtained_item)

    @patch('yummy.managers.date', MockedDate)
    def test_objects_get_actual_returns_nothing_if_not_found(self):

        #monday, odd week
        WeekMenu.objects.create(day=1, even_week=False)

        #monday, even week
        MockedDate.today = classmethod(lambda cls: date(2012, 1, 9))

        obtained_item = WeekMenu.objects.get_actual()

        tools.assert_equals({}, obtained_item)
