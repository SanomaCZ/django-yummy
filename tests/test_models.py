# -*- coding: utf-8 -*-
from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django import VERSION as DJANGO_VERSION

from nose import tools, SkipTest

from yummy.models import Category, Recipe, RecipeRecommendation


class TestRecipeRecommendation(TestCase):

    def setUp(self):
        super(TestRecipeRecommendation, self).setUp()
        cache.clear()

        self.user = User.objects.create_user(username='foo')
        self.cat = Category.objects.create(title="generic cat")
        self.recipe = Recipe.objects.create(
            title='generic recipe',
            category=self.cat,
            preparation_time=20,
            owner=self.user,
            is_approved=True)

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
        self.c0 = Category.objects.create(title="Ámen", slug="amen")
        self.c1 = Category.objects.create(parent=self.c0, title="Mňam mňam", slug="mnam-mnam")

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
        tools.assert_equal("Mňam mňam", "%s" % self.c1.__unicode__())

    def test_select_related(self):
        if DJANGO_VERSION[:2] < (1, 4):
            raise SkipTest()
        self.assertNumQueries(1, lambda: Category.objects.get(slug="mnam-mnam").parent.slug)

    def test_get_absolute_url(self):
        tools.assert_equal('/amen/', self.c0.get_absolute_url())
        tools.assert_equal('/amen/mnam-mnam/', self.c1.get_absolute_url())


class TestRecipeModel(TestCase):

    def setUp(self):
        super(TestRecipeModel, self).setUp()

