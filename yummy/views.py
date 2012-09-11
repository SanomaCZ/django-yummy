from django.http import Http404
from django.views.generic import ListView, DetailView
from django.utils.translation import ugettext, ugettext_lazy as _

from yummy.models import Category, Ingredient, Recipe



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
        print 'cat set'
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
        print 'get qs'
        print self.category
        if self.category:
            qs = qs.filter(category=self.category)
        return qs


class RecipeDetail(DetailView):

    template_name = 'recipe_detail.html'

    model = Recipe

    def get_object(self, queryset=None):
        try:
            return self.model.objects.get(slug=self.kwargs.get('recipe_slug'))
        except self.model.DoesNotExist:
            raise Http404(_("Given recipe not found"))
