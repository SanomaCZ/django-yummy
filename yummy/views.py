from django.http import Http404, HttpResponseRedirect
from django.views.generic import ListView, DetailView, RedirectView, View
from django.utils.translation import ugettext, ugettext_lazy as _
from django.conf import settings

from yummy.models import Category, Ingredient, Recipe

CATEGORY_ORDER_DEFAULT = getattr(settings, 'YUMMY_CATEGORY_ORDER', '-created')
CATEGORY_ORDERING = {
    'slug': _("by ranking"), #TODO - add ranking
    'title': _("by alphabet"),
    '-created': _("by date"),
}
CATEGORY_PHOTO = ('all', 'photos')
CATEGORY_ORDER_ATTR = 'category_order_attr'
CATEGORY_PHOTO_ATTR = 'category_photo_attr'


class IngredientView(ListView):
    template_name = 'ingredient_detail.html'
    model = Recipe

    def set_ingredient(self, slug):
        try:
            self._ingredient = Ingredient.objects.get(slug=slug)
        except Ingredient.DoesNotExist:
            return None
        return self._ingredient

    @property
    def ingredient(self):
        return self._ingredient

    def dispatch(self, request, *args, **kwargs):
        if not self.set_ingredient(kwargs.get('ingredient')):
            raise Http404(ugettext("Ingredient not found"))
        return super(IngredientView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.model.objects.approved().filter(ingredient=self.ingredient)


class CategoryView(ListView):
    template_name = 'category_list.html'
    model = Recipe

    def set_category(self, category_path):
        try:
            self._category = Category.objects.get(path=category_path)
        except Category.DoesNotExist:
            self._category = None
        return self._category

    @property
    def category(self):
        return self._category

    def dispatch(self, request, *args, **kwargs):
        category = kwargs.get('category_path')
        if not self.set_category(category) and category:
            raise Http404(ugettext("Category not found"))
        return super(CategoryView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = self.model.objects.approved()
        if self.category:
            qs = qs.filter(category=self.category)

        photo_attr = self.request.COOKIES.get(CATEGORY_PHOTO_ATTR) or 'all'
        if photo_attr != 'all':
            #TODO - add photo filtering
            #qs = qs.filter()
            pass
        order_attr = self.request.COOKIES.get(CATEGORY_ORDER_ATTR)
        if order_attr not in CATEGORY_ORDERING.keys():
            order_attr = CATEGORY_ORDER_DEFAULT

        qs = qs.order_by(order_attr)
        return qs

    def get_context_data(self, **kwargs):
        data = super(CategoryView, self).get_context_data(**kwargs)
        data['current_order_attr'] = self.request.COOKIES.get(CATEGORY_ORDER_ATTR) or CATEGORY_ORDER_DEFAULT
        data['current_photo_attr'] = self.request.COOKIES.get(CATEGORY_PHOTO_ATTR) or 'all'
        data['ranking_attrs'] = CATEGORY_ORDERING
        return data


class CategoryReorder(View):
    def get(self, request, *args, **kwargs):

        #TODO - check or sign next_url (see Entree)
        next_url =  request.GET.get('next_url') or '/'
        response = HttpResponseRedirect(next_url)

        order_attr = kwargs.get('order_attr') or CATEGORY_ORDER_ATTR
        if request.COOKIES.get(CATEGORY_ORDER_ATTR) != order_attr:
            response.set_cookie(CATEGORY_ORDER_ATTR, order_attr)

        photo_attr = kwargs.get('photo_attr') or 'all'
        if request.COOKIES.get(CATEGORY_PHOTO_ATTR) != photo_attr:
            response.set_cookie(CATEGORY_PHOTO_ATTR, photo_attr)

        return response


class RecipeDetail(DetailView):
    template_name = 'recipe_detail.html'

    model = Recipe

    def get_object(self, queryset=None):
        try:
            return self.model.objects.get(slug=self.kwargs.get('recipe_slug'))
        except self.model.DoesNotExist:
            raise Http404(_("Given recipe not found"))
