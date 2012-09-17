from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect, HttpResponse, HttpResponseNotAllowed
from django.views.generic import ListView, DetailView, View
from django.utils.translation import ugettext
from django.utils.simplejson import dumps

from yummy.models import Category, Ingredient, Recipe, WeekMenu
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
            pass#return HttpResponseNotAllowed("Allowed AJAX request only")

        try:
            day = request.GET['day']
        except (KeyError, ValueError):
            raise Http404

        menu = WeekMenu.objects.get_actual(day)
        if not menu:
            raise Http404

        menu_data = {}
        for one in ('soup', 'meal', 'dessert'):
            try:
                menu_item = getattr(menu, one)
            except AttributeError:
                pass
            else:
                try:
                    image_url = menu_item.get_top_photo().image.url
                except AttributeError:
                    image_url = ''
                menu_data[one] = {
                    'title': menu_item.title,
                    'link': reverse('yummy:recipe_detail', args=(menu_item.category.path, menu_item.slug, menu_item.pk)),
                    'image': image_url,
                }
        return self.render_to_response(menu_data)


class IngredientView(ListView):
    template_name = 'yummy/ingredient_detail.html'
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
    template_name = 'yummy/category_list.html'
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
            print path
            raise Http404("Category with path '%s' not found" % path)
        return super(CategoryView, self).dispatch(request, path, **kwargs)

    def get_queryset(self):
        qs = self.model.objects.approved()
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
        data['current_order_attr'] = self.request.COOKIES.get(conf.CATEGORY_ORDER_ATTR) or conf.CATEGORY_ORDER_DEFAULT
        data['current_photo_attr'] = self.request.COOKIES.get(conf.CATEGORY_PHOTO_ATTR) or 'all'
        data['ranking_attrs'] = conf.CATEGORY_ORDERING
        data['category'] = self.category
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
