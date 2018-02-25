# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import ella.core.cache.fields
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0002_auto_20150520_1709'),
        ('uberyummy', '0001_initial'),
        ('yummy', '0003_auto_20160412_1350'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='tags',
            field=taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', blank=True, help_text='A comma-separated list of tags.', verbose_name='Recipe tags'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='tags_consumer',
            field=taggit.managers.TaggableManager(to='taggit.Tag', through='uberyummy.ConsumerTag', blank=True, help_text='A comma-separated list of tags.', verbose_name='Recipe consumers'),
        ),
        migrations.AlterField(
            model_name='category',
            name='parent',
            field=ella.core.cache.fields.CachedForeignKey(blank=True, to='yummy.Category', null=True),
        ),
        migrations.AlterField(
            model_name='category',
            name='photo',
            field=ella.core.cache.fields.CachedForeignKey(verbose_name='Photo', blank=True, to='yummy.Photo', null=True),
        ),
        migrations.AlterField(
            model_name='cookbook',
            name='owner',
            field=ella.core.cache.fields.CachedForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='cookbookrecipe',
            name='cookbook',
            field=ella.core.cache.fields.CachedForeignKey(to='yummy.CookBook'),
        ),
        migrations.AlterField(
            model_name='cookbookrecipe',
            name='recipe',
            field=ella.core.cache.fields.CachedForeignKey(to='yummy.Recipe'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='group',
            field=ella.core.cache.fields.CachedForeignKey(verbose_name='Group', blank=True, to='yummy.IngredientGroup', null=True),
        ),
        migrations.AlterField(
            model_name='ingredientinrecipe',
            name='group',
            field=ella.core.cache.fields.CachedForeignKey(verbose_name='Group', blank=True, to='yummy.IngredientInRecipeGroup', null=True),
        ),
        migrations.AlterField(
            model_name='ingredientinrecipe',
            name='ingredient',
            field=ella.core.cache.fields.CachedForeignKey(verbose_name='Ingredient', to='yummy.Ingredient'),
        ),
        migrations.AlterField(
            model_name='ingredientinrecipe',
            name='recipe',
            field=ella.core.cache.fields.CachedForeignKey(verbose_name='Recipe', to='yummy.Recipe'),
        ),
        migrations.AlterField(
            model_name='ingredientinrecipegroup',
            name='recipe',
            field=ella.core.cache.fields.CachedForeignKey(verbose_name='Recipe', to='yummy.Recipe'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='category',
            field=ella.core.cache.fields.CachedForeignKey(verbose_name='Category', to='yummy.Category'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='cooking_type',
            field=ella.core.cache.fields.CachedForeignKey(verbose_name='Cooking type', blank=True, to='yummy.CookingType', null=True),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='owner',
            field=ella.core.cache.fields.CachedForeignKey(verbose_name='User', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='servings',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='No. of servings', choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16)]),
        ),
        migrations.AlterField(
            model_name='recipephoto',
            name='photo',
            field=ella.core.cache.fields.CachedForeignKey(verbose_name='Photo', to='yummy.Photo'),
        ),
        migrations.AlterField(
            model_name='recipephoto',
            name='recipe',
            field=ella.core.cache.fields.CachedForeignKey(verbose_name='Recipe', to='yummy.Recipe'),
        ),
        migrations.AlterField(
            model_name='reciperecommendation',
            name='recipe',
            field=ella.core.cache.fields.CachedForeignKey(to='yummy.Recipe'),
        ),
        migrations.AlterField(
            model_name='shoppinglist',
            name='owner',
            field=ella.core.cache.fields.CachedForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='shoppinglistitem',
            name='ingredient',
            field=ella.core.cache.fields.CachedForeignKey(verbose_name='Ingredient', to='yummy.Ingredient'),
        ),
        migrations.AlterField(
            model_name='shoppinglistitem',
            name='shopping_list',
            field=ella.core.cache.fields.CachedForeignKey(to='yummy.ShoppingList'),
        ),
        migrations.AlterField(
            model_name='substituteingredient',
            name='ingredient',
            field=ella.core.cache.fields.CachedForeignKey(verbose_name='Ingredient', to='yummy.Ingredient'),
        ),
        migrations.AlterField(
            model_name='substituteingredient',
            name='substitute',
            field=ella.core.cache.fields.CachedForeignKey(related_name='substitute_ingredients', verbose_name='Substitute ingredient', to='yummy.Ingredient'),
        ),
        migrations.AlterField(
            model_name='weekmenu',
            name='dessert',
            field=ella.core.cache.fields.CachedForeignKey(related_name='menu_dessert', verbose_name='Dessert', blank=True, to='yummy.Recipe', null=True),
        ),
        migrations.AlterField(
            model_name='weekmenu',
            name='meal',
            field=ella.core.cache.fields.CachedForeignKey(related_name='menu_meal', verbose_name='Meal', blank=True, to='yummy.Recipe', null=True),
        ),
        migrations.AlterField(
            model_name='weekmenu',
            name='soup',
            field=ella.core.cache.fields.CachedForeignKey(related_name='menu_soup', verbose_name='Soup', blank=True, to='yummy.Recipe', null=True),
        ),
    ]
