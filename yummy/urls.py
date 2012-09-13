from django.conf.urls import patterns, url
from django.utils.translation import ugettext as _
from django.template.defaultfilters import slugify

from yummy.views import CategoryView, IngredientView, RecipeDetail, CategoryReorder


urlpatterns = patterns('',
    url(r'^%s/(?P<ingredient>[\w-]+)/$' % slugify(_("ingredient")), IngredientView.as_view(), name='ingredient_detail'),
    url(r'^%s/$' % _("ingredient"), IngredientView.as_view(), name='ingredient_index'),  # TODO

    url(r'^(?P<cat_path>[\w/-]+)/(?P<recipe_slug>[\w-]+)-(?P<recipe_id>[\d]+)/$', RecipeDetail.as_view(), name='recipe_detail'),

    url(r'^category_reorder/(?P<order_attr>[\w-]+)/$', CategoryReorder.as_view(), name='category_reorder'),
    url(r'^category_reorder/(?P<order_attr>[\w-]+)/(?P<photo_attr>\w+)/$', CategoryReorder.as_view(), name='category_reorder'),

    url(r'^(?P<path>[\w/-]+)/$', CategoryView.as_view(), name='category_detail'),
    url(r'^$', CategoryView.as_view(), name='category_detail'),
)
