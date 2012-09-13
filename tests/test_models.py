# -*- coding: utf-8 -*-
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django import VERSION as DJANGO_VERSION
from nose import tools, SkipTest

from yummy.models import Category


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

