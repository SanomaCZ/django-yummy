from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.template.defaultfilters import slugify

from yummy.views import (
    CategoryView, IngredientView, RecipeDetail, CategoryReorder, DailyMenu,
    AuthorRecipes, AuthorList, IngredientGroupView, IngredientDetail,
    CuisineView, CategoryDetail, FavoriteRecipeAdd, CookBookList,
    CookBookDetail, CookbookAdd)


INGREDIENT = slugify(_("ingredient"))
COOKBOOK = slugify(_("cookbook"))

urlpatterns = patterns('',
    url(r'^%s/(?P<author_id>[\d]+)/$' % slugify(_("cooks")), AuthorRecipes.as_view(), name='author_recipes'),
    url(r'^%s/$' % slugify(_("cooks")), AuthorList.as_view(), name='authors_list'),

    url(r'^%s/detail/(?P<ingredient>[\w-]+)/$' % INGREDIENT, IngredientDetail.as_view(), name='ingredient_detail'),
    url(r'^%s/group/(?P<group>[\w-]+)/$' % INGREDIENT, IngredientGroupView.as_view(), name='ingredient_group'),
    #url(r'^%s/season/(?P<ingredient>[\w-]+)/$' % INGREDIENT, IngredientView.as_view(), name='ingredient_season'), #TODO
    url(r'^%s/$' % INGREDIENT, IngredientView.as_view(), name='ingredient_index'),

    url(r'^(?P<cat_path>[\w/-]+)/(?P<recipe_slug>[\w-]+)-(?P<recipe_id>[\d]+)/$', RecipeDetail.as_view(), name='recipe_detail'),

    url(r'^daily_menu/$', DailyMenu.as_view(), name='menu_load_data'),

    url(r'^cuisine/(?P<slug>[\w/-]+)/$', CuisineView.as_view(), name='cuisine_detail'),

    url(r'^%s/add/(?P<recipe_id>\d+)/$' % COOKBOOK, FavoriteRecipeAdd.as_view(), name='cookbook_recipe_add'),
    url(r'^%s/new/$' % COOKBOOK, login_required(CookbookAdd.as_view()), name='cookbook_add'),
    url(r'^%s/list/(?P<username>[-\w]+)/$' % COOKBOOK, CookBookList.as_view(), name='cookbook_list'),
    url(r'^%s/list/(?P<username>[-\w]+)/(?P<cookbook>[-\w]+)/$' % COOKBOOK, CookBookDetail.as_view(), name='cookbook_detail'),

    url(r'^category_reorder/(?P<order_attr>[\w-]+)/$', CategoryReorder.as_view(), name='category_reorder'),
    url(r'^category_reorder/(?P<order_attr>[\w-]+)/(?P<photo_attr>\w+)/$', CategoryReorder.as_view(), name='category_reorder'),

    url(r'^category/(?P<path>[\w/-]+)/$', CategoryDetail.as_view(), name='category_detail'),

    url(r'^$', CategoryView.as_view(), name='category_index'),
)
