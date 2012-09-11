from django.conf.urls import patterns, url
from django.utils.translation import ugettext as _

from yummy.views import CategoryView, IngredientView, RecipeDetail


urlpatterns = patterns('',
    url(r'^%s/(?P<category_path>[\w|-]+)/$' % _("category"), CategoryView.as_view(), name='category_detail'),

    url(r'^%s/(?P<ingredient>[\w|-]+)/$' % _("ingredient"), IngredientView.as_view(), name='ingredient_detail'),
    url(r'^%s/$' % _("ingredient"), IngredientView.as_view(), name='ingredient_index'), #TODO

    url(r'^(?P<recipe_slug>[\w|-]+)/$', RecipeDetail.as_view(), name='recipe_detail'),
    url(r'^$', CategoryView.as_view(), name='yummy_index'),
)
