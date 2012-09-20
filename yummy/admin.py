from django.contrib import admin
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from yummy.models import (Category, CookingType, Cuisine, Ingredient,
    IngredientGroup, UnitConversion, Recipe, IngredientInRecipe,
    IngredientInRecipeGroup, Photo, RecipePhoto, RecipeRecommendation, CookBook, WeekMenu, Consumer)


class ApprovedRecipeRaw(ForeignKeyRawIdWidget):

    def url_parameters(self):
        params = super(ApprovedRecipeRaw, self).url_parameters()
        params.update(dict(is_approved=True))
        return params


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


class RecipePhotoInlineAdmin(admin.TabularInline):
    model = RecipePhoto
    raw_id_fields = ('photo', )
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    inlines = [IngredientInRecipeInlineAdmin, IngredientInRecipeGroupInlineAdmin, RecipePhotoInlineAdmin]
    search_fields = ('title',)
    list_filter = ('is_approved', 'category')


class PhotoAdmin(admin.ModelAdmin):

    readonly_fields = ('owner',)
    list_display = ('get_title', 'image', 'is_redaction',)
    list_filter = ('is_redaction', )
    search_fields = ('description', 'title')

    def get_title(self, obj):
        return obj.title or _("No title")

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        obj.is_redaction = True
        return super(PhotoAdmin, self).save_model(request, obj, form, change)


class RecipePhotoAdmin(admin.ModelAdmin):

    raw_id_fields = ('recipe', 'photo',)
    list_display = ('recipe', 'photo', 'is_visible', 'order')
    search_fields = ('recipe__title', )

class RecipeRecommendationAdmin(admin.ModelAdmin):

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        db = kwargs.get('using')
        if db_field.name == 'recipe':
            kwargs['widget'] = ApprovedRecipeRaw(db_field.rel, self.admin_site, using=db)
        return db_field.formfield(**kwargs)


class WeekMenuAdmin(admin.ModelAdmin):

    list_display = ('__unicode__', 'selected_recipes')
    list_filter = ('even_week',)
    ordering = ('even_week', 'day')

    def selected_recipes(self, obj):
        return mark_safe(_("soup: %(soup)s<br>meal: %(meal)s<br>dessert: %(dessert)s") \
                    % dict(soup=obj.soup, meal=obj.meal, dessert=obj.dessert))
    selected_recipes.short_description = _('Selected recipes')
    selected_recipes.allow_tags = True

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        db = kwargs.get('using')
        if db_field.name in ('soup', 'meal', 'dessert'):
            kwargs['widget'] = ApprovedRecipeRaw(db_field.rel, self.admin_site, using=db)
        return db_field.formfield(**kwargs)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Cuisine, CuisineAdmin)
admin.site.register(Photo, PhotoAdmin)
admin.site.register(RecipePhoto, RecipePhotoAdmin)
admin.site.register(RecipeRecommendation, RecipeRecommendationAdmin)
admin.site.register(WeekMenu, WeekMenuAdmin)

admin.site.register([CookingType, Ingredient, IngredientGroup, UnitConversion,
                     IngredientInRecipeGroup, IngredientInRecipe, CookBook, Consumer])
