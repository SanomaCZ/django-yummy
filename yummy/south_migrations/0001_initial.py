# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CookingType'
        db.create_table('yummy_cookingtype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=64)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('yummy', ['CookingType'])

        # Adding model 'Cuisine'
        db.create_table('yummy_cuisine', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=64)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('yummy', ['Cuisine'])

        # Adding model 'IngredientGroup'
        db.create_table('yummy_ingredientgroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=128)),
        ))
        db.send_create_signal('yummy', ['IngredientGroup'])

        # Adding model 'Ingredient'
        db.create_table('yummy_ingredient', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yummy.IngredientGroup'], null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=64)),
            ('genitive', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('default_unit', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('ndb_no', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('yummy', ['Ingredient'])

        # Adding model 'Photo'
        db.create_table('yummy_photo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=64)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('is_redaction', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal('yummy', ['Photo'])

        # Adding model 'Category'
        db.create_table('yummy_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yummy.Category'], null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=64)),
            ('photo', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yummy.Photo'], null=True, blank=True)),
            ('path', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('yummy', ['Category'])

        # Adding model 'Recipe'
        db.create_table('yummy_recipe', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=64)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yummy.Category'])),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('preparation', self.gf('django.db.models.fields.TextField')()),
            ('cooking_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yummy.CookingType'], null=True, blank=True)),
            ('servings', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('price', self.gf('django.db.models.fields.SmallIntegerField')(default=3)),
            ('difficulty', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=3)),
            ('preparation_time', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('caloric_value', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('is_approved', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created', self.gf('django.db.models.fields.DateTimeField')()),
            ('updated', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('yummy', ['Recipe'])

        # Adding M2M table for field cuisines on 'Recipe'
        db.create_table('yummy_recipe_cuisines', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('recipe', models.ForeignKey(orm['yummy.recipe'], null=False)),
            ('cuisine', models.ForeignKey(orm['yummy.cuisine'], null=False))
        ))
        db.create_unique('yummy_recipe_cuisines', ['recipe_id', 'cuisine_id'])

        # Adding model 'IngredientInRecipeGroup'
        db.create_table('yummy_ingredientinrecipegroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('recipe', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yummy.Recipe'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('order', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=1)),
        ))
        db.send_create_signal('yummy', ['IngredientInRecipeGroup'])

        # Adding unique constraint on 'IngredientInRecipeGroup', fields ['recipe', 'order']
        db.create_unique('yummy_ingredientinrecipegroup', ['recipe_id', 'order'])

        # Adding model 'IngredientInRecipe'
        db.create_table('yummy_ingredientinrecipe', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('recipe', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yummy.Recipe'])),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yummy.IngredientInRecipeGroup'], null=True, blank=True)),
            ('ingredient', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yummy.Ingredient'])),
            ('amount', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=5, decimal_places=2, blank=True)),
            ('unit', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=1)),
            ('note', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal('yummy', ['IngredientInRecipe'])

        # Adding model 'RecipeOfDay'
        db.create_table('yummy_recipeofday', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')(unique=True)),
            ('recipe', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yummy.Recipe'])),
        ))
        db.send_create_signal('yummy', ['RecipeOfDay'])

        # Adding model 'UnitConversion'
        db.create_table('yummy_unitconversion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('from_unit', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('to_unit', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('ratio', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=5)),
        ))
        db.send_create_signal('yummy', ['UnitConversion'])

        # Adding unique constraint on 'UnitConversion', fields ['from_unit', 'to_unit']
        db.create_unique('yummy_unitconversion', ['from_unit', 'to_unit'])


    def backwards(self, orm):
        # Removing unique constraint on 'UnitConversion', fields ['from_unit', 'to_unit']
        db.delete_unique('yummy_unitconversion', ['from_unit', 'to_unit'])

        # Removing unique constraint on 'IngredientInRecipeGroup', fields ['recipe', 'order']
        db.delete_unique('yummy_ingredientinrecipegroup', ['recipe_id', 'order'])

        # Deleting model 'CookingType'
        db.delete_table('yummy_cookingtype')

        # Deleting model 'Cuisine'
        db.delete_table('yummy_cuisine')

        # Deleting model 'IngredientGroup'
        db.delete_table('yummy_ingredientgroup')

        # Deleting model 'Ingredient'
        db.delete_table('yummy_ingredient')

        # Deleting model 'Photo'
        db.delete_table('yummy_photo')

        # Deleting model 'Category'
        db.delete_table('yummy_category')

        # Deleting model 'Recipe'
        db.delete_table('yummy_recipe')

        # Removing M2M table for field cuisines on 'Recipe'
        db.delete_table('yummy_recipe_cuisines')

        # Deleting model 'IngredientInRecipeGroup'
        db.delete_table('yummy_ingredientinrecipegroup')

        # Deleting model 'IngredientInRecipe'
        db.delete_table('yummy_ingredientinrecipe')

        # Deleting model 'RecipeOfDay'
        db.delete_table('yummy_recipeofday')

        # Deleting model 'UnitConversion'
        db.delete_table('yummy_unitconversion')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'yummy.category': {
            'Meta': {'object_name': 'Category'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yummy.Category']", 'null': 'True', 'blank': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'photo': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yummy.Photo']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '64'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'yummy.cookingtype': {
            'Meta': {'object_name': 'CookingType'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '64'})
        },
        'yummy.cuisine': {
            'Meta': {'object_name': 'Cuisine'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '64'})
        },
        'yummy.ingredient': {
            'Meta': {'object_name': 'Ingredient'},
            'default_unit': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'genitive': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yummy.IngredientGroup']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'ndb_no': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '64'})
        },
        'yummy.ingredientgroup': {
            'Meta': {'object_name': 'IngredientGroup'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '128'})
        },
        'yummy.ingredientinrecipe': {
            'Meta': {'object_name': 'IngredientInRecipe'},
            'amount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yummy.IngredientInRecipeGroup']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ingredient': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yummy.Ingredient']"}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            'recipe': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yummy.Recipe']"}),
            'unit': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'yummy.ingredientinrecipegroup': {
            'Meta': {'unique_together': "(('recipe', 'order'),)", 'object_name': 'IngredientInRecipeGroup'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            'recipe': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yummy.Recipe']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'})
        },
        'yummy.photo': {
            'Meta': {'object_name': 'Photo'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'is_redaction': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '64'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'yummy.recipe': {
            'Meta': {'object_name': 'Recipe'},
            'caloric_value': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yummy.Category']"}),
            'cooking_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yummy.CookingType']", 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {}),
            'cuisines': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['yummy.Cuisine']", 'symmetrical': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'difficulty': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '3'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_approved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'preparation': ('django.db.models.fields.TextField', [], {}),
            'preparation_time': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'price': ('django.db.models.fields.SmallIntegerField', [], {'default': '3'}),
            'servings': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '64'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {})
        },
        'yummy.recipeofday': {
            'Meta': {'object_name': 'RecipeOfDay'},
            'date': ('django.db.models.fields.DateField', [], {'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recipe': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yummy.Recipe']"})
        },
        'yummy.unitconversion': {
            'Meta': {'unique_together': "(('from_unit', 'to_unit'),)", 'object_name': 'UnitConversion'},
            'from_unit': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ratio': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '5'}),
            'to_unit': ('django.db.models.fields.PositiveSmallIntegerField', [], {})
        }
    }

    complete_apps = ['yummy']