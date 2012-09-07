# -*- coding: utf-8 -*-
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from nose import tools

from yummy.models import Category


class TestCategoryModel(TestCase):

    def setUp(self):
        super(TestCategoryModel, self).setUp()
        self.c0 = Category.objects.create(title="Ámen", slug="amen")
        self.c1 = Category.objects.create(parent=self.c0, title="Mňam mňam", slug="mnam-mnam")

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
