from datetime import date
from django.core.cache import cache
from django.template import Template, Context
from django.test import TestCase

from mock import patch

from yummy.models import WeekMenu
from yummy.templatetags.yummy_tags import yummy_day_menu

from nose import tools


class MockedDate(date):
    pass


class TestTags(TestCase):

    def setUp(self):
        cache.clear()


    def test_yummy_menu_context_items(self):
        context = yummy_day_menu()

        tools.assert_equals(context['current_menu'], {})
        tools.assert_equals(type(context['week_days']), tuple)

    @patch('yummy.managers.date', MockedDate)
    @patch('yummy.templatetags.yummy_tags.date', MockedDate)
    def test_yummy_renders_current_menu(self):
        #monday odd week
        actual_item = WeekMenu.objects.create(day=1, even_week=False)

        #monday, odd week
        MockedDate.today = classmethod(lambda cls: date(2012, 1, 2))

        context = yummy_day_menu()

        tools.assert_equals(context['current_menu'], actual_item)

    @patch('yummy.managers.date', MockedDate)
    @patch('yummy.templatetags.yummy_tags.date', MockedDate)
    def test_yummy_renders_empty_item(self):
        #monday odd week
        actual_item = WeekMenu.objects.create(day=1, even_week=False)

        #monday, even week
        MockedDate.today = classmethod(lambda cls: date(2012, 1, 9))

        context = yummy_day_menu()

        tools.assert_equals(context['current_menu'], {})

    def test_recommendation_renders_even_without_data(self):
        c = Context()
        t = Template("{% load yummy_tags %}{% yummy_recipe_recommendation as recommends %}")
        t.render(c)

        tools.assert_equals(c['recommends'], tuple())

    def test_recommendation_with_count_renders_even_without_data(self):
        c = Context()
        t = Template("{% load yummy_tags %}{% yummy_recipe_recommendation 4 as recommends %}")
        t.render(c)

        tools.assert_equals(c['recommends'], tuple())
