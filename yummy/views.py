from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect, HttpResponse, HttpResponseNotAllowed
from django.views.generic import ListView, DetailView, View
from django.utils.simplejson import dumps

from yummy.models import Category, Ingredient, Recipe, WeekMenu, IngredientGroup, IngredientInRecipe, Cuisine
from yummy import conf
from yummy.utils import import_module_member

FUNC_QS_BY_RATING = conf.FUNC_QS_BY_RATING
if FUNC_QS_BY_RATING:
    FUNC_QS_BY_RATING = import_module_member(FUNC_QS_BY_RATING)


class JSONResponseMixin(object):
    def render_to_response(self, context):
        return self.get_json_response(self.convert_context_to_json(context))

    def get_json_response(self, content, **kwargs):
        return HttpResponse(content, content_type='application/json', **kwargs)

    def convert_context_to_json(self, context):
        return dumps(context, ensure_ascii=False)


class CynosureList(ListView):

    context_cynosure_name = 'cynosure'

    @property
    def cynosure(self):
        return self._cynosure

    def get_cynosure(self):
        raise NotImplementedError("Override get_cynosure in %s! Now!" % self.__class__.__name__)

    def get(self, request, *args, **kwargs):
        try:
            self.get_cynosure()
        except ObjectDoesNotExist:
            raise Http404("Page not found")
        return super(CynosureList, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super(CynosureList, self).get_context_data(**kwargs)
        COOKIES = self.request.COOKIES
        current_order_attr = COOKIES.get(conf.CATEGORY_ORDER_ATTR)
        if current_order_attr not in dict(conf.CATEGORY_ORDERING).keys():
            current_order_attr = conf.CATEGORY_ORDER_DEFAULT

        current_photo_attr = COOKIES.get(conf.CATEGORY_PHOTO_ATTR)
        if current_photo_attr not in conf.CATEGORY_PHOTO_OPTIONS:
            current_photo_attr = conf.CATEGORY_PHOTO_OPTIONS[0]

        data.update({
            'current_order_attr': current_order_attr,
            'current_photo_attr': current_photo_attr,
            'ranking_attrs': conf.CATEGORY_ORDERING,
            self.context_cynosure_name: self.cynosure,
        })
        return data


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


class IngredientGroupView(CynosureList):

    template_name = 'yummy/ingredient/group.html'
    model = Ingredient

    def get_queryset(self):
        return self.model.objects.filter(group=self.cynosure)

    def get_cynosure(self):
        self._cynosure = IngredientGroup.objects.get(slug=self.kwargs['group'])


class IngredientDetail(CynosureList):

    template_name = 'yummy/ingredient/detail.html'
    model = IngredientInRecipe

    def get_queryset(self):
        return self.model.objects.filter(ingredient=self.cynosure).select_related('recipe')

    def get_cynosure(self):
        self._cynosure = Ingredient.objects.get(slug=self.kwargs['ingredient'])


class OrderListView(ListView):
    def get_context_data(self, **kwargs):
        data = super(OrderListView, self).get_context_data(**kwargs)
        data.update({
            'current_order_attr': self.request.COOKIES.get(conf.CATEGORY_ORDER_ATTR) or conf.CATEGORY_ORDER_DEFAULT,
            'current_photo_attr': self.request.COOKIES.get(conf.CATEGORY_PHOTO_ATTR) or 'all',
            'ranking_attrs': conf.CATEGORY_ORDERING,
            'all_recipes_count': Recipe.objects.public().count(),
        })
        return data


class CategoryView(OrderListView):
    template_name = 'yummy/category/index.html'
    model = Recipe

    def get_queryset(self):
        qs = self.model.objects.public()

        photo_attr = self.request.COOKIES.get(conf.CATEGORY_PHOTO_ATTR) or 'all'
        if photo_attr != 'all':
            #TODO - add photo filtering
            #qs = qs.filter()
            pass
        order_attr = self.request.COOKIES.get(conf.CATEGORY_ORDER_ATTR)
        if order_attr not in conf.CATEGORY_ORDERING.keys():
            order_attr = conf.CATEGORY_ORDER_DEFAULT
        
        if order_attr == 'by_rating' and FUNC_QS_BY_RATING:
            qs = FUNC_QS_BY_RATING(qs)
        else:
            qs = qs.order_by(order_attr)
        return qs


class CategoryDetail(CynosureList, CategoryView):
    template_name = 'yummy/category/detail.html'

    def get_cynosure(self):
        self._cynosure = Category.objects.get(path=self.kwargs['path'])

    def get_queryset(self):
        qs = super(CategoryDetail, self).get_queryset()
        qs = qs.filter(category=self.cynosure)
        return qs


class CategoryReorder(View):
    def get(self, request, *args, **kwargs):
        #TODO - check or sign next_url (see Entree)
        next_url = request.GET.get('next_url') or '/'
        response = HttpResponseRedirect(next_url)

        order_attr = kwargs.get('order_attr')
        if order_attr not in conf.CATEGORY_ORDERING:
            order_attr = conf.CATEGORY_ORDER_DEFAULT

        if request.COOKIES.get(conf.CATEGORY_ORDER_ATTR) != order_attr:
            response.set_cookie(conf.CATEGORY_ORDER_ATTR, order_attr)

        photo_attr = kwargs.get('photo_attr')
        if photo_attr not in conf.CATEGORY_PHOTO_OPTIONS:
            photo_attr = conf.CATEGORY_PHOTO_OPTIONS[0]
        if request.COOKIES.get(conf.CATEGORY_PHOTO_ATTR) != photo_attr:
            response.set_cookie(conf.CATEGORY_PHOTO_ATTR, photo_attr)

        return response


class RecipeDetail(DetailView):
    template_name = 'yummy/recipe/detail.html'

    model = Recipe

    def get_object(self, queryset=None):
        try:
            return self.model.objects.get(pk=self.kwargs.get('recipe_id'), slug=self.kwargs.get('recipe_slug'))
        except self.model.DoesNotExist:
            raise Http404("Given recipe not found")


class AuthorRecipes(CynosureList):

    template_name = 'yummy/recipe/author.html'
    model = Recipe

    def get_cynosure(self):
        self._cynosure = User.objects.get(pk=self.kwargs['author_id'])

    def get_queryset(self):
        return self.model.objects.public().filter(owner=self.cynosure)


class CuisineView(CynosureList):

    model = Recipe
    template_name = 'yummy/recipe/cuisine.html'

    def get_cynosure(self):
        self._cynosure = Cuisine.objects.get(slug=self.kwargs['slug'])

    def get_queryset(self):
        return Recipe.objects.public().filter(cuisines__in=[self.cynosure])


class AuthorList(OrderListView):
    model = User
    template_name = 'yummy/cook/list.html'

    def get_queryset(self):
        return User.objects.filter(recipe__is_approved=True).distinct()
