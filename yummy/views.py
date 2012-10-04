from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect, HttpResponse, HttpResponseNotAllowed
from django.views.generic import ListView, DetailView, View
from django.utils.translation import ugettext
from django.utils.simplejson import dumps

from yummy.models import Category, Ingredient, Recipe, WeekMenu, IngredientGroup, IngredientInRecipe
from yummy import conf


class JSONResponseMixin(object):
    def render_to_response(self, context):
        return self.get_json_response(self.convert_context_to_json(context))

    def get_json_response(self, content, **kwargs):
        return HttpResponse(content, content_type='application/json', **kwargs)

    def convert_context_to_json(self, context):
        return dumps(context, ensure_ascii=False)


class DailyMenu(JSONResponseMixin, View):

    def get(self, request, *args, **kwargs):

        if not request.is_ajax():
            return HttpResponseNotAllowed("Allowed AJAX request only")

        menu_days = WeekMenu.objects.get_actual()
        menu_data = dict( [(one, {}) for one in range(1,8)] )
        for day_index, day_menu in menu_days.items():
            menu_data[day_index] = self.arrange_menu_item(day_menu)

        return self.render_to_response(menu_data)

    def arrange_menu_item(self, menu_item):
        arranged_item = {}
        for one in ('soup', 'meal', 'dessert'):
            try:
                actual_item = getattr(menu_item, one)
            except AttributeError:
                arranged_item[one] = {}
            else:
                try:
                    image_url = actual_item.get_top_photo().image.url
                except AttributeError:
                    image_url = ''

                arranged_item[one] = {
                    'title': actual_item.title,
                    'link': reverse('yummy:recipe_detail', args=(
                        actual_item.category.path, actual_item.slug, actual_item.pk)),
                    'image': image_url,
                }

        return arranged_item


class IngredientView(ListView):

    template_name = 'yummy/ingredient/index.html'
    model = Ingredient

    def get_context_data(self, **kwargs):
        data = super(IngredientView, self).get_context_data(**kwargs)

        data.update({
            'groups': IngredientGroup.objects.all(),
            'months': conf.MONTHS,
        })

        return data


class IngredientGroupView(ListView):

    template_name = 'yummy/ingredient/group.html'
    model = Ingredient

    def set_group(self, slug):
        try:
            self._group = IngredientGroup.objects.get(slug=slug)
        except Ingredient.DoesNotExist:
            return None
        return self._group

    @property
    def group(self):
        return self._group

    def dispatch(self, request, *args, **kwargs):
        if not self.set_group(kwargs.get('group')):
            raise Http404(ugettext("Group not found"))
        return super(IngredientGroupView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super(IngredientGroupView, self).get_context_data(**kwargs)
        data.update({
            'group': self.group,
        })
        return data

    def get_queryset(self):
        return self.model.objects.filter(group=self.group)


class IngredientDetail(ListView):

    template_name = 'yummy/ingredient/detail.html'
    model = IngredientInRecipe

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
        return super(IngredientDetail, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super(IngredientDetail, self).get_context_data(**kwargs)
        data.update({
            'ingredient': self.ingredient,
        })
        return data

    def get_queryset(self):
        return self.model.objects.filter(ingredient=self.ingredient).select_related('recipe')


class CategoryView(ListView):
    template_name = 'yummy/category/list.html'
    model = Recipe

    def set_category(self, path):
        try:
            self._category = Category.objects.get(path=path)
        except Category.DoesNotExist:
            self._category = None
        return self._category

    @property
    def category(self):
        return self._category

    def dispatch(self, request, path=None, **kwargs):
        if not self.set_category(path) and path is not None:
            raise Http404("Category with path '%s' not found" % path)
        return super(CategoryView, self).dispatch(request, path, **kwargs)

    def get_queryset(self):
        qs = self.model.objects.public()
        if self.category:
            qs = qs.filter(category=self.category)

        photo_attr = self.request.COOKIES.get(conf.CATEGORY_PHOTO_ATTR) or 'all'
        if photo_attr != 'all':
            #TODO - add photo filtering
            #qs = qs.filter()
            pass
        order_attr = self.request.COOKIES.get(conf.CATEGORY_ORDER_ATTR)
        if order_attr not in conf.CATEGORY_ORDERING.keys():
            order_attr = conf.CATEGORY_ORDER_DEFAULT

        qs = qs.order_by(order_attr)
        return qs

    def get_context_data(self, **kwargs):
        data = super(CategoryView, self).get_context_data(**kwargs)
        data.update({
            'current_order_attr': self.request.COOKIES.get(conf.CATEGORY_ORDER_ATTR) or conf.CATEGORY_ORDER_DEFAULT,
            'current_photo_attr': self.request.COOKIES.get(conf.CATEGORY_PHOTO_ATTR) or 'all',
            'ranking_attrs': conf.CATEGORY_ORDERING,
            'category': self.category,

        })
        return data


class CategoryReorder(View):
    def get(self, request, *args, **kwargs):

        #TODO - check or sign next_url (see Entree)
        next_url = request.GET.get('next_url') or '/'
        response = HttpResponseRedirect(next_url)

        order_attr = kwargs.get('order_attr') or conf.CATEGORY_ORDER_ATTR
        if request.COOKIES.get(conf.CATEGORY_ORDER_ATTR) != order_attr:
            response.set_cookie(conf.CATEGORY_ORDER_ATTR, order_attr)

        photo_attr = kwargs.get('photo_attr') or 'all'
        if request.COOKIES.get(conf.CATEGORY_PHOTO_ATTR) != photo_attr:
            response.set_cookie(conf.CATEGORY_PHOTO_ATTR, photo_attr)

        return response


class RecipeDetail(DetailView):
    template_name = 'yummy/recipe_detail.html'

    model = Recipe

    def get_object(self, queryset=None):
        try:
            return self.model.objects.get(pk=self.kwargs.get('recipe_id'), slug=self.kwargs.get('recipe_slug'))
        except self.model.DoesNotExist:
            raise Http404("Given recipe not found")


class AuthorRecipes(ListView):

    template_name = 'yummy/author_recipes.html'
    model = Recipe

    def get(self, request, *args, **kwargs):
        try:
            self.owner = User.objects.get(pk=self.kwargs['author_id'])
        except User.DoesNotExist:
            raise Http404("Given author not found")
        return super(AuthorRecipes, self).get(request, *args, **kwargs)

    def get_queryset(self):
        return self.model.objects.public().filter(owner=self.owner)

    def get_context_data(self, **kwargs):
        data = super(AuthorRecipes, self).get_context_data(**kwargs)
        data.update({
            'current_order_attr': self.request.COOKIES.get(conf.CATEGORY_ORDER_ATTR) or conf.CATEGORY_ORDER_DEFAULT,
            'current_photo_attr': self.request.COOKIES.get(conf.CATEGORY_PHOTO_ATTR) or 'all',
            'ranking_attrs': conf.CATEGORY_ORDERING,
            'author': self.owner,
        })
        return data
