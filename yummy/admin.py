from django.contrib import admin

from yummy.models import (Category, CookingType, Cuisine, Ingredient,
    IngredientGroup, UnitConversion, Recipe, IngredientInRecipe,
    IngredientInRecipeGroup, Photo, RecipePhoto)


class CuisineAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}


class IngredientInRecipeInlineAdmin(admin.TabularInline):
    model = IngredientInRecipe
    extra = 1


class IngredientInRecipeGroupInlineAdmin(admin.TabularInline):
    model = IngredientInRecipeGroup
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    inlines = [IngredientInRecipeInlineAdmin, IngredientInRecipeGroupInlineAdmin]
    exclude_fields = ('group',)
    search_fields = ('title', )


class PhotoAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        return super(PhotoAdmin, self).save_model(request, obj, form, change)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Cuisine, CuisineAdmin)
admin.site.register(Photo, PhotoAdmin)

admin.site.register([Photo, CookingType, Ingredient, IngredientGroup, UnitConversion,
                     IngredientInRecipeGroup, IngredientInRecipe, RecipePhoto])
