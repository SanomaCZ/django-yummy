from datetime import datetime

from django.db import models
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from yummy import conf
from yummy.managers import RecipeManager, CategoryManager


class CookingType(models.Model):

    name = models.CharField(_('Name'), max_length=128)
    slug = models.SlugField(_('Slug'), max_length=64, unique=True)
    description = models.TextField(_('Description'), blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Cooking type')
        verbose_name_plural = _('Cooking types')


class Cuisine(models.Model):

    name = models.CharField(_('Name'), max_length=128)
    slug = models.SlugField(_('Slug'), max_length=64, unique=True)
    description = models.TextField(_('Description'), blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Cuisine')
        verbose_name_plural = _('Cuisines')


class IngredientGroup(models.Model):

    name = models.CharField(_('Name'), max_length=128)
    slug = models.SlugField(_('Slug'), max_length=128, unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Ingredient group')
        verbose_name_plural = _('Ingredient groups')


class Ingredient(models.Model):

    group = models.ForeignKey(IngredientGroup, verbose_name=_('Group'), null=True, blank=True)
    name = models.CharField(_('Name'), max_length=128)
    slug = models.SlugField(_('Slug'), max_length=64, unique=True)
    genitive = models.CharField(_('Genitive'), max_length=128, blank=True)
    default_unit = models.PositiveSmallIntegerField(choices=conf.UNIT_CHOICES, verbose_name=_('Default unit'))

    ndb_no = models.IntegerField(_('NDB id number'), blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Ingredient')
        verbose_name_plural = _('Ingredients')


class Photo(models.Model):

    # FIXME: smarter callable upload_to
    image = models.ImageField(_('Image'), upload_to="photos/%Y/%m/%d")
    title = models.CharField(_('Title'), max_length=64)
    slug = models.SlugField(_('Slug'), max_length=64)
    description = models.TextField(_('Description'), blank=True)
    is_redaction = models.BooleanField(default=False)

    owner = models.ForeignKey(User, editable=False)

    class Meta:
        verbose_name = _('Photo')
        verbose_name_plural = _('Photos')


class Category(models.Model):

    objects = CategoryManager()

    parent = models.ForeignKey('self', null=True, blank=True)
    title = models.CharField(_('Title'), max_length=128)
    slug = models.SlugField(_('Slug'), max_length=64)
    # fake recipe photo
    photo = models.ForeignKey(Photo, verbose_name=_('Photo'), null=True, blank=True)
    path = models.CharField(max_length=255, editable=False, unique=True)
    description = models.TextField(_('Description'), blank=True)

    def __unicode__(self):
        return self.title

    @property
    def is_root_category(self):
        return self.parent is None

    def is_ancestor_of(self, category=None):
        if category is None or category.is_root_category:
            return False
        if category.parent == self:
            return True
        return self.is_ancestor_of(category.parent)

    def get_children(self):
        return self.__class__.objects.filter(parent=self)

    def get_descendants(self):
        descendants = ()
        for child_category in self.get_children():
            descendants += (child_category,)
            descendants += child_category.get_descendants()
        return descendants

    @property
    def level(self):
        return len(self.path.split('/'))

    def path_is_unique(self):
        if self.parent:
            path = '%s/%s' % (self.parent.path, self.slug)
        else:
            path = self.slug
        try:
            self.__class__.objects.get(path=path)
        except self.__class__.DoesNotExist:
            return True
        else:
            return False

    def clean(self):
        if self == self.parent:
            raise ValidationError(_('Parent category must be different than child.'))

        if self.is_ancestor_of(self.parent):
            raise ValidationError(_('A parent can\'t be a descendant of this category.'))

        if not self.path_is_unique():
            raise ValidationError(_('Path is not unique, change category title or slug.'))

    def save(self, **kwargs):
        "Override save() to construct path based on the category's parent."
        old_path = self.path

        if self.parent:
            if self == self.parent or self.is_ancestor_of(self.parent):
                raise IntegrityError('Bad category structure. Check category parent.')
            self.path = '%s/%s' % (self.parent.path, self.slug)
        else:
            self.path = self.slug

        super(Category, self).save(**kwargs)

        if old_path != self.path and self.get_children().count() > 0:
            # update descendants
            for cat in self.get_descendants():
                cat.save(force_update=True)

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')


class Recipe(models.Model):

    objects = RecipeManager()

    title = models.CharField(_('Title'), max_length=128)
    slug = models.SlugField(_('Slug'), max_length=64, unique=True)
    category = models.ForeignKey(Category, verbose_name=_("Category"))

    description = models.TextField(_('Short description'), blank=True)
    preparation = models.TextField(_('Preparation'))

    cooking_type = models.ForeignKey(CookingType, verbose_name=_('Cooking type'), blank=True, null=True)
    cuisines = models.ManyToManyField(Cuisine, verbose_name=_('Cuisines'))
    servings = models.PositiveSmallIntegerField(_('Servings'), blank=True, null=True)

    price = models.SmallIntegerField(_('Price'), choices=conf.PRICING_CHOICES, default=3, db_index=True)
    difficulty = models.PositiveSmallIntegerField(_('Preparation difficulty'), choices=conf.DIFFICULTY_CHOICES, default=3, db_index=True)
    preparation_time = models.PositiveSmallIntegerField(_('Preparation time (min)'))
    caloric_value = models.PositiveIntegerField(_('Caloric value'), blank=True, null=True)

    owner = models.ForeignKey(User, verbose_name=_('User'))
    is_approved = models.BooleanField(_('Approved'), default=False, db_index=True)
    created = models.DateTimeField(editable=False)
    updated = models.DateTimeField(editable=False)

    def __unicode__(self):
        return self.title

    def save(self, **kwargs):
        if not self.id:
            self.created = datetime.now()
        self.updated = datetime.now()
        super(Recipe, self).save(**kwargs)

    class Meta:
        verbose_name = _('Recipe')
        verbose_name_plural = _('Recipes')


class IngredientInRecipeGroup(models.Model):

    recipe = models.ForeignKey(Recipe, verbose_name=_('Recipe'))
    title = models.CharField(_('Title'), max_length=128, blank=True)
    description = models.TextField(_('Short description'), blank=True)
    order = models.PositiveSmallIntegerField(_('Order'), default=1)

    def __unicode__(self):
        return u"%s %s" % (self.recipe, self.title)

    class Meta:
        unique_together = (('recipe', 'order'),)
        verbose_name = _('Ingredients in recipe group')
        verbose_name_plural = _('Ingredients in recipe groups')


class IngredientInRecipe(models.Model):

    recipe = models.ForeignKey(Recipe, verbose_name=_('Recipe'))
    group = models.ForeignKey(IngredientInRecipeGroup, verbose_name=_('Group'), null=True, blank=True)
    ingredient = models.ForeignKey(Ingredient, verbose_name=_('Ingredient'))
    amount = models.DecimalField(_('Amount'), max_digits=5, decimal_places=2, null=True, blank=True)
    unit = models.PositiveSmallIntegerField(_('Unit'), choices=conf.UNIT_CHOICES, null=True, blank=True)
    order = models.PositiveSmallIntegerField(_('Order'), default=1, db_index=True)
    note = models.CharField(_('Note'), max_length=255, blank=True)

    def __unicode__(self):
        return u"%s - %s" % (self.ingredient, self.recipe)

    class Meta:
        unique_together = (('recipe', 'order'),)
        verbose_name = _('Ingredient in recipe')
        verbose_name_plural = _('Ingredients in recipe')


class UnitConversion(models.Model):

    from_unit = models.PositiveSmallIntegerField(choices=conf.UNIT_CHOICES)
    to_unit = models.PositiveSmallIntegerField(choices=conf.UNIT_CHOICES)
    ratio = models.DecimalField(_('Ratio'), max_digits=10, decimal_places=5)

    def __unicode__(self):
        return u"1%s = %s%s" % (self.from_unit, self.ratio, self.to_unit)

    class Meta:
        unique_together = (('from_unit', 'to_unit',),)
        verbose_name = _('Unit conversion')
        verbose_name_plural = _('Units conversions')
