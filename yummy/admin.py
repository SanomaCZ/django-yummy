from django.contrib import admin

from yummy.models import (Category, CookingType, Cuisine, Ingredient,
                          IngredientGroup, UnitConversion)

admin.site.register([Category, CookingType, Cuisine, Ingredient,
                     IngredientGroup, UnitConversion])
