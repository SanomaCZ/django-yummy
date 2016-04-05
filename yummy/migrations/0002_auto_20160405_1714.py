# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yummy', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubstituteIngredient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ingredient', models.ForeignKey(verbose_name='Ingredient', to='yummy.Ingredient')),
                ('substitute', models.ForeignKey(related_name='substitute_ingredients', verbose_name='Substitute ingredient', to='yummy.Ingredient')),
            ],
            options={
                'verbose_name': 'Substitute ingredient',
                'verbose_name_plural': 'Substitute ingredients',
            },
        ),
    ]
