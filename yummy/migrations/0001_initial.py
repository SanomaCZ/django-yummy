# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import yummy.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=128, verbose_name='Title')),
                ('slug', models.SlugField(max_length=64, verbose_name='Slug')),
                ('path', models.CharField(unique=True, max_length=255, editable=False)),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('parent', models.ForeignKey(blank=True, to='yummy.Category', null=True)),
            ],
            options={
                'ordering': (b'path',),
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CookBook',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=128, verbose_name='Title')),
                ('slug', models.SlugField(max_length=128, verbose_name='Slug')),
                ('is_public', models.BooleanField(default=True, verbose_name='Public')),
                ('is_default', models.BooleanField(default=False, verbose_name='Default cookbook')),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Cookbook',
                'verbose_name_plural': 'Cookbooks',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CookBookRecipe',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('note', models.CharField(max_length=255, verbose_name='Note', blank=True)),
                ('added', models.DateField(verbose_name='Added')),
                ('cookbook', models.ForeignKey(to='yummy.CookBook')),
            ],
            options={
                'verbose_name': "Cookbooks' recipes",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CookingType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128, verbose_name='Name')),
                ('slug', models.SlugField(unique=True, max_length=64, verbose_name='Slug')),
                ('description', models.TextField(verbose_name='Description', blank=True)),
            ],
            options={
                'verbose_name': 'Cooking type',
                'verbose_name_plural': 'Cooking types',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Cuisine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128, verbose_name='Name')),
                ('slug', models.SlugField(unique=True, max_length=64, verbose_name='Slug')),
                ('description', models.TextField(verbose_name='Description', blank=True)),
            ],
            options={
                'verbose_name': 'Cuisine',
                'verbose_name_plural': 'Cuisines',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128, verbose_name='Name')),
                ('slug', models.SlugField(unique=True, max_length=64, verbose_name='Slug')),
                ('genitive', models.CharField(max_length=128, verbose_name='Genitive', blank=True)),
                ('default_unit', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Default unit', choices=[(0, 'piece'), (1, 'gram'), (2, 'dekagram'), (3, 'kilogram'), (4, 'mililiter'), (5, 'deciliter'), (6, 'liter'), (7, 'packaging'), (8, 'package'), (9, 'part'), (10, 'cup'), (11, 'handful'), (12, 'drop'), (13, 'crubicle'), (14, 'can'), (15, 'scoop'), (16, 'cube'), (17, 'ball'), (18, 'bottle'), (19, 'spoon'), (20, 'teaspoon'), (21, 'bowl'), (22, 'bud'), (23, 'slice'), (24, 'tin'), (25, 'jar'), (26, 'sprig'), (27, 'clove'), (28, 'bunch'), (29, 'crumb'), (30, 'teacup'), (31, 'twig'), (32, 'serving'), (33, 'leaf'), (34, 'microphyll'), (35, 'batch')])),
                ('ndb_no', models.IntegerField(null=True, verbose_name='NDB id number', blank=True)),
                ('is_approved', models.BooleanField(default=True, db_index=True, verbose_name='Approved')),
            ],
            options={
                'verbose_name': 'Ingredient',
                'verbose_name_plural': 'Ingredients',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IngredientGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128, verbose_name='Name')),
                ('slug', models.SlugField(unique=True, max_length=128, verbose_name='Slug')),
            ],
            options={
                'verbose_name': 'Ingredient group',
                'verbose_name_plural': 'Ingredient groups',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='ingredient',
            name='group',
            field=models.ForeignKey(verbose_name='Group', blank=True, to='yummy.IngredientGroup', null=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='IngredientInRecipe',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.DecimalField(null=True, verbose_name='Amount', max_digits=5, decimal_places=2, blank=True)),
                ('unit', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Unit', choices=[(0, 'piece'), (1, 'gram'), (2, 'dekagram'), (3, 'kilogram'), (4, 'mililiter'), (5, 'deciliter'), (6, 'liter'), (7, 'packaging'), (8, 'package'), (9, 'part'), (10, 'cup'), (11, 'handful'), (12, 'drop'), (13, 'crubicle'), (14, 'can'), (15, 'scoop'), (16, 'cube'), (17, 'ball'), (18, 'bottle'), (19, 'spoon'), (20, 'teaspoon'), (21, 'bowl'), (22, 'bud'), (23, 'slice'), (24, 'tin'), (25, 'jar'), (26, 'sprig'), (27, 'clove'), (28, 'bunch'), (29, 'crumb'), (30, 'teacup'), (31, 'twig'), (32, 'serving'), (33, 'leaf'), (34, 'microphyll'), (35, 'batch')])),
                ('order', models.PositiveSmallIntegerField(db_index=True, verbose_name='Order', blank=True)),
                ('note', models.CharField(max_length=255, verbose_name='Note', blank=True)),
                ('ingredient', models.ForeignKey(verbose_name='Ingredient', to='yummy.Ingredient')),
            ],
            options={
                'verbose_name': 'Ingredient in recipe',
                'verbose_name_plural': 'Ingredients in recipe',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IngredientInRecipeGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=128, verbose_name='Title')),
                ('description', models.TextField(verbose_name='Short description', blank=True)),
                ('order', models.PositiveSmallIntegerField(db_index=True, verbose_name='Order', blank=True)),
            ],
            options={
                'verbose_name': 'Ingredients in recipe group',
                'verbose_name_plural': 'Ingredients in recipe groups',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='ingredientinrecipe',
            name='group',
            field=models.ForeignKey(verbose_name='Group', blank=True, to='yummy.IngredientInRecipeGroup', null=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', models.ImageField(height_field=b'height', upload_to=yummy.models.upload_to, width_field=b'width', max_length=255, verbose_name='Image')),
                ('width', models.PositiveIntegerField(editable=False)),
                ('height', models.PositiveIntegerField(editable=False)),
                ('title', models.CharField(max_length=64, verbose_name='Title', blank=True)),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('is_redaction', models.BooleanField(default=False, editable=False)),
                ('created', models.DateTimeField(editable=False)),
                ('owner', models.ForeignKey(editable=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Photo',
                'verbose_name_plural': 'Photos',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='category',
            name='photo',
            field=models.ForeignKey(verbose_name='Photo', blank=True, to='yummy.Photo', null=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=128, verbose_name='Title')),
                ('slug', models.SlugField(unique=True, max_length=64, verbose_name='Slug')),
                ('description', models.TextField(verbose_name='Short description', blank=True)),
                ('preparation', models.TextField(verbose_name='Preparation')),
                ('hint', models.TextField(verbose_name='Hint', blank=True)),
                ('servings', models.PositiveSmallIntegerField(null=True, verbose_name='No. of servings', blank=True)),
                ('price', models.SmallIntegerField(default=3, choices=[(1, 'Cheapest'), (2, 'Cheaper'), (3, 'Standard price'), (4, 'Expensive'), (5, 'Most Expensive')], blank=True, null=True, verbose_name='Price', db_index=True)),
                ('difficulty', models.PositiveSmallIntegerField(default=3, choices=[(1, 'Easy'), (3, 'Standard difficulty'), (5, 'Difficult')], blank=True, null=True, verbose_name='Preparation difficulty', db_index=True)),
                ('preparation_time', models.PositiveSmallIntegerField(null=True, verbose_name='Preparation time (min)', blank=True)),
                ('caloric_value', models.PositiveIntegerField(null=True, verbose_name='Caloric value', blank=True)),
                ('is_approved', models.BooleanField(default=False, db_index=True, verbose_name='Approved')),
                ('is_public', models.BooleanField(default=True, verbose_name='Public')),
                ('is_checked', models.BooleanField(default=False, verbose_name='Is checked')),
                ('created', models.DateTimeField(editable=False)),
                ('updated', models.DateTimeField(editable=False)),
                ('category', models.ForeignKey(verbose_name='Category', to='yummy.Category')),
                ('cooking_type', models.ForeignKey(verbose_name='Cooking type', blank=True, to='yummy.CookingType', null=True)),
                ('cuisines', models.ManyToManyField(to='yummy.Cuisine', verbose_name='Cuisines', blank=True)),
                ('owner', models.ForeignKey(verbose_name='User', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Recipe',
                'verbose_name_plural': 'Recipes',
                'permissions': ((b'approve_recipe', b'Can approve recipe'),),
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='ingredientinrecipegroup',
            name='recipe',
            field=models.ForeignKey(verbose_name='Recipe', to='yummy.Recipe'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ingredientinrecipe',
            name='recipe',
            field=models.ForeignKey(verbose_name='Recipe', to='yummy.Recipe'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cookbookrecipe',
            name='recipe',
            field=models.ForeignKey(to='yummy.Recipe'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='cookbookrecipe',
            unique_together=set([(b'cookbook', b'recipe')]),
        ),
        migrations.AddField(
            model_name='cookbook',
            name='recipes',
            field=models.ManyToManyField(to='yummy.Recipe', verbose_name='Recipes', through='yummy.CookBookRecipe'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='cookbook',
            unique_together=set([(b'owner', b'slug')]),
        ),
        migrations.CreateModel(
            name='RecipePhoto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_visible', models.BooleanField(default=True, verbose_name='Visible')),
                ('is_checked', models.BooleanField(default=False, verbose_name='Checked')),
                ('order', models.PositiveSmallIntegerField(db_index=True, verbose_name='Order', blank=True)),
                ('photo', models.ForeignKey(verbose_name='Photo', to='yummy.Photo')),
                ('recipe', models.ForeignKey(verbose_name='Recipe', to='yummy.Recipe')),
            ],
            options={
                'verbose_name': 'Recipe photo',
                'verbose_name_plural': 'Recipe photos',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='recipephoto',
            unique_together=set([(b'recipe', b'order'), (b'recipe', b'photo')]),
        ),
        migrations.CreateModel(
            name='RecipeRecommendation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('day_from', models.DateField(help_text='Recipe will show itself starting this day', verbose_name='Show from day')),
                ('day_to', models.DateField(help_text='Recipe shown until this day. This field is not required. The longer is recipe shown, the lower priority it has.', null=True, verbose_name='Show until day (inclusive)', blank=True)),
                ('recipe', models.ForeignKey(to='yummy.Recipe')),
            ],
            options={
                'verbose_name': 'Recipe recommendation',
                'verbose_name_plural': 'Recipe recommendations',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ShoppingList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=155, verbose_name='Title')),
                ('note', models.TextField(verbose_name='Note', blank=True)),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Shopping list',
                'verbose_name_plural': 'Shopping lists',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ShoppingListItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.DecimalField(null=True, verbose_name='Amount', max_digits=5, decimal_places=2, blank=True)),
                ('unit', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Unit', choices=[(0, 'piece'), (1, 'gram'), (2, 'dekagram'), (3, 'kilogram'), (4, 'mililiter'), (5, 'deciliter'), (6, 'liter'), (7, 'packaging'), (8, 'package'), (9, 'part'), (10, 'cup'), (11, 'handful'), (12, 'drop'), (13, 'crubicle'), (14, 'can'), (15, 'scoop'), (16, 'cube'), (17, 'ball'), (18, 'bottle'), (19, 'spoon'), (20, 'teaspoon'), (21, 'bowl'), (22, 'bud'), (23, 'slice'), (24, 'tin'), (25, 'jar'), (26, 'sprig'), (27, 'clove'), (28, 'bunch'), (29, 'crumb'), (30, 'teacup'), (31, 'twig'), (32, 'serving'), (33, 'leaf'), (34, 'microphyll'), (35, 'batch')])),
                ('note', models.CharField(max_length=255, verbose_name='Note', blank=True)),
                ('ingredient', models.ForeignKey(verbose_name='Ingredient', to='yummy.Ingredient')),
                ('shopping_list', models.ForeignKey(to='yummy.ShoppingList')),
            ],
            options={
                'verbose_name': 'Shopping list item',
                'verbose_name_plural': 'Shopping list items',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='shoppinglistitem',
            unique_together=set([(b'shopping_list', b'ingredient')]),
        ),
        migrations.CreateModel(
            name='UnitConversion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('from_unit', models.PositiveSmallIntegerField(choices=[(0, 'piece'), (1, 'gram'), (2, 'dekagram'), (3, 'kilogram'), (4, 'mililiter'), (5, 'deciliter'), (6, 'liter'), (7, 'packaging'), (8, 'package'), (9, 'part'), (10, 'cup'), (11, 'handful'), (12, 'drop'), (13, 'crubicle'), (14, 'can'), (15, 'scoop'), (16, 'cube'), (17, 'ball'), (18, 'bottle'), (19, 'spoon'), (20, 'teaspoon'), (21, 'bowl'), (22, 'bud'), (23, 'slice'), (24, 'tin'), (25, 'jar'), (26, 'sprig'), (27, 'clove'), (28, 'bunch'), (29, 'crumb'), (30, 'teacup'), (31, 'twig'), (32, 'serving'), (33, 'leaf'), (34, 'microphyll'), (35, 'batch')])),
                ('to_unit', models.PositiveSmallIntegerField(choices=[(0, 'piece'), (1, 'gram'), (2, 'dekagram'), (3, 'kilogram'), (4, 'mililiter'), (5, 'deciliter'), (6, 'liter'), (7, 'packaging'), (8, 'package'), (9, 'part'), (10, 'cup'), (11, 'handful'), (12, 'drop'), (13, 'crubicle'), (14, 'can'), (15, 'scoop'), (16, 'cube'), (17, 'ball'), (18, 'bottle'), (19, 'spoon'), (20, 'teaspoon'), (21, 'bowl'), (22, 'bud'), (23, 'slice'), (24, 'tin'), (25, 'jar'), (26, 'sprig'), (27, 'clove'), (28, 'bunch'), (29, 'crumb'), (30, 'teacup'), (31, 'twig'), (32, 'serving'), (33, 'leaf'), (34, 'microphyll'), (35, 'batch')])),
                ('ratio', models.DecimalField(verbose_name='Ratio', max_digits=10, decimal_places=5)),
            ],
            options={
                'verbose_name': 'Unit conversion',
                'verbose_name_plural': 'Units conversions',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='unitconversion',
            unique_together=set([(b'from_unit', b'to_unit')]),
        ),
        migrations.CreateModel(
            name='WeekMenu',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('day', models.IntegerField(verbose_name='Day of the week', choices=[(1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thursday'), (5, 'Friday'), (6, 'Saturday'), (7, 'Sunday')])),
                ('even_week', models.BooleanField(default=False, help_text='Check if this day menu is for even week. Current week is even.', verbose_name='Menu for even week')),
                ('dessert', models.ForeignKey(blank=True, to='yummy.Recipe', null=True)),
                ('meal', models.ForeignKey(blank=True, to='yummy.Recipe', null=True)),
                ('soup', models.ForeignKey(blank=True, to='yummy.Recipe', null=True)),
            ],
            options={
                'verbose_name': 'Menu of the day',
                'verbose_name_plural': 'Menus of the day',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='weekmenu',
            unique_together=set([(b'day', b'even_week')]),
        ),
    ]
