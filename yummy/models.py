from os import path
from hashlib import md5
from datetime import date

from django.db import models
from django.db import IntegrityError
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.utils.encoding import smart_str
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.utils.translation.trans_real import ugettext

from yummy import conf
from yummy import managers


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


def upload_to(instance, filename):
    name, ext = path.splitext(filename)
    to_hash = '|'.join((name, now().strftime('%Y-%m-%d %H:%M:%S'), smart_str(instance.owner)))
    h = md5(to_hash).hexdigest()

    return path.join(
        "yummy",
        h[:2],
        h[2:4],
        h + ext.lower()
    )


class Photo(models.Model):

    image = models.ImageField(_('Image'), upload_to=upload_to, max_length=255,
                              width_field='width', height_field='height')
    width = models.PositiveIntegerField(editable=False)
    height = models.PositiveIntegerField(editable=False)
    title = models.CharField(_('Title'), max_length=64, blank=True)
    description = models.TextField(_('Description'), blank=True)
    is_redaction = models.BooleanField(default=False, editable=False)

    owner = models.ForeignKey(User, editable=False)

    def __unicode__(self):
        return self.image.url

    class Meta:
        verbose_name = _('Photo')
        verbose_name_plural = _('Photos')


class Category(models.Model):

    objects = managers.CategoryManager()

    parent = models.ForeignKey('self', null=True, blank=True)
    title = models.CharField(_('Title'), max_length=128)
    slug = models.SlugField(_('Slug'), max_length=64)
    # fake recipe photo
    photo = models.ForeignKey(Photo, verbose_name=_('Photo'), null=True, blank=True)
    path = models.CharField(max_length=255, editable=False, unique=True)
    description = models.TextField(_('Description'), blank=True)

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('yummy:category_detail', args=(self.path,))

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

        if old_path != self.path and self.get_children().count():
            # update descendants
            for cat in self.get_descendants():
                cat.save(force_update=True)

    @property
    def photo_hierarchic(self):
        if self.photo:
            return self.photo
        if self.parent:
            return self.parent.photo_hierarchic


class Consumer(models.Model):
    """
    Some recipes are suitable for diabetics, kids etc. for example
    """

    title = models.CharField(_('Title'), max_length=64)
    slug = models.SlugField(_('Slug'), max_length=64, unique=True)

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _("Consumer")
        verbose_name_plural = _("Consumers")


class Recipe(models.Model):

    objects = managers.RecipeManager()

    title = models.CharField(_('Title'), max_length=128)
    slug = models.SlugField(_('Slug'), max_length=64, unique=True)
    category = models.ForeignKey(Category, verbose_name=_("Category"))

    description = models.TextField(_('Short description'), blank=True)
    preparation = models.TextField(_('Preparation'))
    hint = models.TextField(_('Hint'), blank=True)

    cooking_type = models.ForeignKey(CookingType, verbose_name=_('Cooking type'), blank=True, null=True)
    cuisines = models.ManyToManyField(Cuisine, verbose_name=_('Cuisines'))
    servings = models.PositiveSmallIntegerField(_('Servings'), blank=True, null=True)
    consumers = models.ManyToManyField(Consumer, verbose_name=_('Consumers'), blank=True)

    price = models.SmallIntegerField(_('Price'), choices=conf.PRICING_CHOICES, default=3, db_index=True)
    difficulty = models.PositiveSmallIntegerField(_('Preparation difficulty'), choices=conf.DIFFICULTY_CHOICES, default=3, db_index=True)
    preparation_time = models.PositiveSmallIntegerField(_('Preparation time (min)'))
    caloric_value = models.PositiveIntegerField(_('Caloric value'), blank=True, null=True)

    owner = models.ForeignKey(User, verbose_name=_('User'))
    is_approved = models.BooleanField(_('Approved'), default=False, db_index=True)
    is_public = models.BooleanField(_('Public'), default=True)
    created = models.DateTimeField(editable=False)
    updated = models.DateTimeField(editable=False)

#    photos = models.ManyToManyField(Photo, verbose_name=_('Photos'), through='RecipePhoto')

    def __unicode__(self):
        return self.title

    def save(self, **kwargs):
        self.updated = now()
        if not self.id:
            self.created = self.updated
        super(Recipe, self).save(**kwargs)

    class Meta:
        verbose_name = _('Recipe')
        verbose_name_plural = _('Recipes')
        permissions = (
            ("approve_recipe", "Can approve recipe"),
        )

    def get_photos(self):
        return tuple(p.photo for p in self.recipephoto_set.visible().order_by('order'))

    def get_top_photo(self, recache=False):
        """
        Get to photo for recipe. Prefer photo from recipe's owner, if available.
        If recipe doesn't have any photo, try to get photo for recipe's category

        :return: photo for recipe
        :rtype: Photo
        """
        cache_key = '%s_recipe_top_photo' % self.pk
        cached_photo = cache.get(cache_key)
        if cached_photo is None or recache:
            photos = self.get_photos()
            if photos:
                cached_photo = photos[0]
            else:
                cached_photo = self.category.photo_hierarchic

            cache.set(cache_key, cached_photo, timeout=conf.CACHE_TOP_PHOTO)
        return cached_photo


class RecipePhoto(models.Model):

    objects = managers.RecipePhotoManager()

    recipe = models.ForeignKey(Recipe, verbose_name=_('Recipe'))
    photo = models.ForeignKey(Photo, verbose_name=_('Photo'))
    is_visible = models.BooleanField(_('Visible'), default=True)
    order = models.PositiveSmallIntegerField(_('Order'), default=1, db_index=True)

    def __unicode__(self):
        return u"%d. %s" % (self.order, self.photo)

    class Meta:
        unique_together = (
            ('recipe', 'photo'),
            ('recipe', 'order'),
        )
        verbose_name = _('Recipe photo')
        verbose_name_plural = _('Recipe photos')

    def save(self, *args, **kwargs):
        if self.photo.owner_id == self.recipe.owner_id:
            self.manage_photo_order()

        super(RecipePhoto, self).save(*args, **kwargs)

        self.recipe.get_top_photo(recache=True)

    def manage_photo_order(self):
        """
        update photo's order if current photo belongs to recipe's owner:

        - set current photo `order` value as lowest owner's but higher than non-owners
        - if this value collides, bump following values
            (also make there a gap to fit more photos w/o reordering in there)
        """
        photos = list(RecipePhoto.objects.filter(recipe=self.recipe).order_by('order'))
        if not photos:
            return

        last_owners_order_value = 0
        following_photo_index = 0

        #look for last owner's photo to set `order` value for current instance
        for loop_index, one in enumerate(photos):
            if one.photo.owner_id == self.recipe.owner_id:
                last_owners_order_value = one.order
            elif last_owners_order_value:
                following_photo_index = loop_index
                break

        self.order = last_owners_order_value + 1

        #now deal with colliding ids, if any
        if photos[following_photo_index].order > self.order:
            return

        last_order_value = self.order
        modified_items = []
        for loop_index, one in enumerate(photos[following_photo_index:]):
            if one.order > last_order_value:
                #seems like ids don't collide anymore
                break

            order_bump = conf.PHOTO_ORDER_GAP if loop_index == 0 else 1
            one.order = last_order_value + order_bump
            last_order_value = one.order
            modified_items.append(one)

        #save items later, due to unique_together
        for one in modified_items[::-1]:
            one.save()



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


class RecipeRecommendation(models.Model):

    objects = managers.RecipeRecommendationManager()

    day_from = models.DateField(_("Show from day"), help_text=_("Recipe will show itself starting this day"))
    day_to = models.DateField(_("Show until day (inclusive)"), blank=True, null=True,
                              help_text=_("Recipe shown until this day. This field is not required. "
                                            "The longer is recipe shown, the lower priority it has."))
    recipe = models.ForeignKey(Recipe)

    def __unicode__(self):
        return u"'%s', %s - %s" % (self.recipe, self.day_from, (self.day_to or _('until forever')))

    class Meta:
        verbose_name = _("Recipe recommendation")
        verbose_name_plural = _("Recipe recommendations")

    def clean(self):
        if not self.recipe.is_approved:
            raise ValidationError(_("You can save recommendation only with approved recipe"))

        if self.day_to and self.day_to < self.day_from:
            raise ValidationError(_("Invalid chronology of border dates"))

    def save(self, *args, **kwargs):
        try:
            self.clean()
        except ValidationError, e:
            raise IntegrityError(e.messages)

        super(RecipeRecommendation, self).save(*args, **kwargs)


class CookBook(models.Model):

    owner = models.ForeignKey(User)
    title = models.CharField(_("Title"), max_length=128)
    slug = models.SlugField(_("Slug"), max_length=128)
    is_public = models.BooleanField(_("Public"), default=True)
    recipes = models.ManyToManyField(Recipe, verbose_name=_('Recipes'))

    def __unicode__(self):
        return u"%s's cookbok: %s" % (self.owner, self.title)

    class Meta:
        unique_together = (('owner', 'slug'),)
        verbose_name = _('Cookbook')
        verbose_name_plural = _('Cookbooks')


class WeekMenu(models.Model):

    day = models.IntegerField(_("Day of the week"), choices=conf.WEEK_DAYS)
    soup = models.ForeignKey(Recipe, blank=True, null=True, related_name="menu_soup")
    meal = models.ForeignKey(Recipe, blank=True, null=True, related_name="menu_meal")
    dessert = models.ForeignKey(Recipe, blank=True, null=True, related_name="menu_dessert")
    even_week = models.BooleanField(_("Menu for even week"), default=False,
                                    help_text=_("Check if this day menu is for even week. Current week is %s." % \
                                                ugettext("odd" if date.isocalendar(date.today())[1] % 2 else "even")))

    objects = managers.WeekMenuManager()

    class Meta:
        unique_together = (('day', 'even_week'),)
        verbose_name = _("Menu of the day")
        verbose_name_plural = _("Menus of the day")

    def __unicode__(self):
        return u"%s week, day %s" % (_("Even") if self.even_week else _("Odd"), self.get_day_display())
