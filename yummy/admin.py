from django.contrib import admin
from django.contrib.admin import RelatedFieldListFilter
from django.contrib.admin.widgets import ForeignKeyRawIdWidget, RelatedFieldWidgetWrapper
from django.forms.widgets import Media
from django.contrib.admin.templatetags.admin_static import static
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from yummy.forms import SubstituteIngredientAdminForm
from yummy.models import (
    Category,
    CookingType,
    Cuisine,
    Ingredient,
    IngredientGroup,
    UnitConversion,
    Recipe,
    IngredientInRecipe,
    IngredientInRecipeGroup,
    Photo,
    RecipePhoto,
    RecipeRecommendation,
    CookBook,
    WeekMenu,
    ShoppingList,
    ShoppingListItem,
    SubstituteIngredient,
)


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
    raw_id_fields = ('group', 'ingredient')

    def get_queryset(self, request):
        parent = super(IngredientInRecipeInlineAdmin, self)
        queryset_method = hasattr(parent, 'get_queryset') and getattr(parent, 'get_queryset') or getattr(parent, 'queryset')
        return queryset_method(request).select_related()

    # backward compatibility
    queryset = get_queryset


class CustomRelatedFieldWidgetWrapper(RelatedFieldWidgetWrapper):

    @property
    def media(self):
        media = Media(js=[static('yummy/js/custom-related-widget-wrapper.js')])
        return self.widget.media + media


class IngredientInRecipeGroupAdmin(admin.ModelAdmin):
    model = IngredientInRecipeGroup

    def formfield_for_dbfield(self, db_field, **kwargs):

        if db_field.name == 'recipe':

            request = kwargs.pop("request", None)

            formfield = self.formfield_for_foreignkey(db_field, request, **kwargs)

            related_modeladmin = self.admin_site._registry.get(db_field.rel.to)

            wrapper_kwargs = {}
            if related_modeladmin:
                wrapper_kwargs.update(
                    can_add_related=related_modeladmin.has_add_permission(request),
                    can_change_related=related_modeladmin.has_change_permission(request),
                    can_delete_related=related_modeladmin.has_delete_permission(request),
                )
            formfield.widget = CustomRelatedFieldWidgetWrapper(
                formfield.widget, db_field.rel, self.admin_site, **wrapper_kwargs
            )
        else:
            formfield = super(IngredientInRecipeGroupAdmin, self).formfield_for_dbfield(db_field, **kwargs)

        return formfield

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'recipe':
            db = kwargs.get('using')
            kwargs['widget'] = ForeignKeyRawIdWidget(db_field.rel, self.admin_site, using=db)
            return db_field.formfield(**kwargs)
        else:
            return super(IngredientInRecipeGroupAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

class RecipePhotoInlineAdmin(admin.TabularInline):
    model = RecipePhoto
    raw_id_fields = ('photo', )
    extra = 1

    def get_queryset(self, request):
        parent = super(RecipePhotoInlineAdmin, self)
        queryset_method = hasattr(parent, 'get_queryset') and getattr(parent, 'get_queryset') or getattr(parent, 'queryset')
        return queryset_method(request).select_related()

    # backward compatibility
    queryset = get_queryset


class RecipeAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    inlines = [IngredientInRecipeInlineAdmin, RecipePhotoInlineAdmin]
    search_fields = ('title',)
    list_filter = ('is_approved', 'is_public', 'is_checked', ('category__path', SubCategoryFilter))
    list_display = ('title', 'category', 'is_approved', 'is_public')
    raw_id_fields = ('owner',)

    actions = ['set_checked']

    def set_checked(self, request, queryset):
        queryset.update(is_checked=True)
    set_checked.short_description = _("Mark given photos as checked")

    def lookup_allowed(self, lookup, value):
        # see https://code.djangoproject.com/ticket/19182
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


class SubstituteIngredientInlineAdmin(admin.TabularInline):
    model = SubstituteIngredient
    form = SubstituteIngredientAdminForm
    fk_name = 'ingredient'
    raw_id_fields = ('substitute',)
    extra = 1


class IngredientAdmin(admin.ModelAdmin):

    prepopulated_fields = {'slug': ('name',)}
    inlines = [SubstituteIngredientInlineAdmin]


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
admin.site.register(IngredientInRecipeGroup, IngredientInRecipeGroupAdmin)

admin.site.register([CookingType, UnitConversion, IngredientInRecipe, CookBook,
                     ShoppingList, ShoppingListItem])
