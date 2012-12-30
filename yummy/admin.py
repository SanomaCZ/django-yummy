from django.contrib import admin
from django.contrib.admin import RelatedFieldListFilter
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from yummy.models import (Category, CookingType, Cuisine, Ingredient,
    IngredientGroup, UnitConversion, Recipe, IngredientInRecipe,
    IngredientInRecipeGroup, Photo, RecipePhoto, RecipeRecommendation,
    CookBook, WeekMenu)


class SubCategoryFilter(RelatedFieldListFilter):

    def __init__(self, field, request, params, model, model_admin, field_path):
        other_model = Category
        self.lookup_kwarg = 'category__path__istartswith'
        self.lookup_kwarg_isnull = 'foo' #not sure what to use here
        self.lookup_val = request.GET.get(self.lookup_kwarg, None)
        self.lookup_val_isnull = request.GET.get(self.lookup_kwarg_isnull, None)

        self.lookup_choices = tuple((one.path, one.title) for one in Category.objects.filter(parent__isnull=True))
        super(RelatedFieldListFilter, self).__init__(
            field, request, params, model, model_admin, field_path)
        if hasattr(field, 'verbose_name'):
            self.lookup_title = field.verbose_name
        else:
            self.lookup_title = other_model._meta.verbose_name
        self.title = self.lookup_title


class ApprovedRecipeRaw(ForeignKeyRawIdWidget):

    def url_parameters(self):
        params = super(ApprovedRecipeRaw, self).url_parameters()
        params.update(dict(is_approved=True))
        return params


class PublicRecipeRaw(ApprovedRecipeRaw):

    def url_parameters(self):
        params = super(PublicRecipeRaw, self).url_parameters()
        params.update(dict(is_public=True))
        return params


class CuisineAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('photo',)
    list_display = ('title', 'chained_title', )
    list_display_links = list_display
    ordering = ('path',)
    search_fields = ('title',)


class IngredientInRecipeInlineAdmin(admin.TabularInline):
    model = IngredientInRecipe
    extra = 1

    def queryset(self, request):
        return super(IngredientInRecipeInlineAdmin, self).queryset(request).select_related()


class IngredientInRecipeGroupInlineAdmin(admin.TabularInline):
    model = IngredientInRecipeGroup
    extra = 1

    def queryset(self, request):
        return super(IngredientInRecipeGroupInlineAdmin, self).queryset(request).select_related()


class RecipePhotoInlineAdmin(admin.TabularInline):
    model = RecipePhoto
    raw_id_fields = ('photo', )
    extra = 1

    def queryset(self, request):
        return super(RecipePhotoInlineAdmin, self).queryset(request).select_related()


class RecipeAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    inlines = [IngredientInRecipeInlineAdmin, RecipePhotoInlineAdmin]
    search_fields = ('title',)
    list_filter = ('is_approved', 'is_public', 'is_checked', ('category__path', SubCategoryFilter))
    list_display = ('title', 'category', 'is_approved', 'is_public')
    actions = ['set_checked']

    def set_checked(self, request, queryset):
        queryset.update(is_checked=True)
    set_checked.short_description = _("Mark given photos as checked")

    def lookup_allowed(self, lookup, value):
        #see https://code.djangoproject.com/ticket/19182
        if lookup == 'category__path__istartswith':
            return True
        return super(RecipeAdmin, self).lookup_allowed(lookup, value)


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

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        db = kwargs.get('using')
        if db_field.name == 'recipe':
            kwargs['widget'] = PublicRecipeRaw(db_field.rel, self.admin_site, using=db)
        return db_field.formfield(**kwargs)


class WeekMenuAdmin(admin.ModelAdmin):

    list_display = ('__unicode__', 'selected_recipes')
    list_filter = ('even_week',)
    ordering = ('even_week', 'day')

    def selected_recipes(self, obj):
        return mark_safe(
            """%(soup_label)s: %(soup)s<br/>
            %(meal_label)s: %(meal)s<br/>
            %(dessert_label)s: %(dessert)s""") %\
               dict(
                   soup=obj.soup,
                   meal=obj.meal,
                   dessert=obj.dessert,
                   soup_label=_("Soup"),
                   meal_label=_("Meal"),
                   dessert_label=_("Dessert")
            )
    selected_recipes.short_description = _('Selected recipes')
    selected_recipes.allow_tags = True

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        db = kwargs.get('using')
        if db_field.name in ('soup', 'meal', 'dessert'):
            kwargs['widget'] = PublicRecipeRaw(db_field.rel, self.admin_site, using=db)
        return db_field.formfield(**kwargs)


class IngredientAdmin(admin.ModelAdmin):

    prepopulated_fields = {'slug': ('name',)}


class IngredientGroupAdmin(admin.ModelAdmin):

    prepopulated_fields = {'slug': ('name',)}


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Cuisine, CuisineAdmin)
admin.site.register(Photo, PhotoAdmin)
admin.site.register(RecipePhoto, RecipePhotoAdmin)
admin.site.register(RecipeRecommendation, RecipeRecommendationAdmin)
admin.site.register(WeekMenu, WeekMenuAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientGroup, IngredientGroupAdmin)

admin.site.register([CookingType, UnitConversion, IngredientInRecipeGroup, IngredientInRecipe, CookBook])
