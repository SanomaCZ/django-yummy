from django.contrib import admin
from django.forms.models import ModelChoiceField

from yummy.models import (Category, CookingType, Cuisine, Ingredient,
    IngredientGroup, UnitConversion, Recipe, IngredientInRecipe,
    IngredientInRecipeGroup, Photo, RecipePhoto, RecipeRecommendation, CookBook)


class CuisineAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('photo',)


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

    readonly_fields = ('owner',)

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        obj.is_redaction = True
        return super(PhotoAdmin, self).save_model(request, obj, form, change)


class RecipeRecommendationAdmin(admin.ModelAdmin):

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "recipe":
            queryset = Recipe.objects.approved()
            return ModelChoiceField(queryset, **kwargs)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Cuisine, CuisineAdmin)
admin.site.register(Photo, PhotoAdmin)
admin.site.register(RecipeRecommendation, RecipeRecommendationAdmin)

admin.site.register([CookingType, Ingredient, IngredientGroup, UnitConversion,
                     IngredientInRecipeGroup, IngredientInRecipe, RecipePhoto, CookBook])
