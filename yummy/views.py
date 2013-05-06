from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.forms import forms
from django.http import (
    Http404, HttpResponseRedirect, HttpResponse, HttpResponseNotAllowed,
    HttpResponseForbidden
)
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.generic import ListView, DetailView, View, CreateView, UpdateView, DeleteView
from django.template.defaultfilters import slugify
from django.utils.simplejson import dumps
from django.utils.translation import ugettext_lazy as _
from django.views.generic.detail import SingleObjectTemplateResponseMixin

from yummy.forms import FavoriteRecipeForm, CookBookAddForm, CookBookDeleteForm, CookBookEditForm
from yummy.models import (
    Category, Ingredient, Recipe, WeekMenu, IngredientGroup, IngredientInRecipe,
    Cuisine, CookBookRecipe, CookBook, ShoppingList, ShoppingListItem
)
from yummy import conf
from yummy.utils import import_module_member


FUNC_QS_BY_RATING = conf.FUNC_QS_BY_RATING
if FUNC_QS_BY_RATING:
    FUNC_QS_BY_RATING = import_module_member(FUNC_QS_BY_RATING)

GET_THUMBNAIL_FUNC = conf.GET_THUMBNAIL_FUNC
if GET_THUMBNAIL_FUNC:
    GET_THUMBNAIL_FUNC = import_module_member(GET_THUMBNAIL_FUNC)
else:
    GET_THUMBNAIL_FUNC = lambda img: img


class JSONResponseMixin(object):
    def render_to_response(self, context):
        return self.get_json_response(self.convert_context_to_json(context))

    def get_json_response(self, content, **kwargs):
        return HttpResponse(content, content_type='application/json', **kwargs)

    def convert_context_to_json(self, context):
        return dumps(context, ensure_ascii=False)


class CynosureList(ListView):

    context_cynosure_name = 'cynosure'
    paginate_by = conf.LISTING_PAGINATE_BY

    @property
    def cynosure(self):
        return self._cynosure

    def get_cynosure(self):
        raise NotImplementedError("Override get_cynosure in %s! Now!" % self.__class__.__name__)

    def get(self, request, *args, **kwargs):
        try:
            self._cynosure = self.get_cynosure()
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
            actual_item = getattr(menu_item, one)
            if not actual_item:
                continue

            try:
                image_url = GET_THUMBNAIL_FUNC(actual_item.get_top_photo().image).url
            except AttributeError:
                image_url = ''

            arranged_item[one] = {
                'title': actual_item.title,
                'link': actual_item.get_absolute_url(),
                'image': image_url,
            }

        return arranged_item


class IngredientView(ListView):

    template_name = 'yummy/ingredient/index.html'
    model = Ingredient
    paginate_by = conf.LISTING_PAGINATE_BY

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
        return IngredientGroup.objects.get(slug=self.kwargs['group'])


class IngredientDetail(CynosureList):

    template_name = 'yummy/ingredient/detail.html'
    model = IngredientInRecipe

    def get_queryset(self):
        return Recipe.objects.filter(ingredientinrecipe__ingredient=self.cynosure).distinct()

    def get_cynosure(self):
        return Ingredient.objects.get(slug=self.kwargs['ingredient'])


class OrderListView(ListView):
    paginate_by = conf.LISTING_PAGINATE_BY

    def get_objects_count(self):
        return Recipe.objects.public().count()
        
    def get_context_data(self, **kwargs):
        data = super(OrderListView, self).get_context_data(**kwargs)
        data.update({
            'current_order_attr': self.request.COOKIES.get(conf.CATEGORY_ORDER_ATTR) or conf.CATEGORY_ORDER_DEFAULT,
            'current_photo_attr': self.request.COOKIES.get(conf.CATEGORY_PHOTO_ATTR) or 'all',
            'ranking_attrs': conf.CATEGORY_ORDERING,
            'all_recipes_count': self.get_objects_count(),
        })
        return data


class CategoryView(OrderListView):
    template_name = 'yummy/category/index.html'
    model = Recipe

    def get_queryset(self):
        qs = self.model.objects.public()
        qs = self.order_queryset(qs)
        return qs

    def order_queryset(self, qs):
        photo_attr = self.request.COOKIES.get(conf.CATEGORY_PHOTO_ATTR) or 'all'
        if photo_attr != 'all':
            qs = qs.filter(recipephoto__isnull=False).distinct()

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
    paginate_by = conf.LISTING_PAGINATE_BY

    def get_cynosure(self):
        return Category.objects.get(path=self.kwargs['path'])

    def get_queryset(self):
        qs = super(CategoryDetail, self).get_queryset()
        subcats = [self.cynosure] + self.cynosure.get_descendants()
        qs = qs.filter(category__in=subcats)
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

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object.is_public and self.object.owner != self.request.user:
            response = render_to_string("yummy/recipe/private.html",
                                        self.get_context_data(),
                                        context_instance=RequestContext(request))
            return HttpResponseForbidden(response)

        return super(RecipeDetail, self).get(request, *args, **kwargs)


class AuthorRecipes(CynosureList):

    template_name = 'yummy/recipe/author.html'
    model = Recipe

    def get_cynosure(self):
        return User.objects.get(pk=self.kwargs['author_id'])

    def get_queryset(self):
        return self.model.objects.public().filter(owner=self.cynosure)


class CuisineView(CynosureList):

    model = Recipe
    template_name = 'yummy/recipe/cuisine.html'

    def get_cynosure(self):
        return Cuisine.objects.get(slug=self.kwargs['slug'])

    def get_queryset(self):
        return Recipe.objects.public().filter(cuisines=self.cynosure)


class AuthorList(OrderListView):
    model = User
    template_name = 'yummy/cook/list.html'

    def get_queryset(self):
        return User.objects.filter(recipe__is_approved=True).distinct()


class FavoriteRecipeAdd(CreateView):

    form_class = FavoriteRecipeForm
    template_name = 'yummy/cookbook/fill.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseForbidden(_("This function is available to logged users only"))
        return super(FavoriteRecipeAdd, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(FavoriteRecipeAdd, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        data = super(FavoriteRecipeAdd, self).get_context_data(**kwargs)
        data['recipe_id'] = self.kwargs['recipe_id']
        return data

    def get_initial(self):
        return {
            'recipe': self.kwargs['recipe_id']
        }

    def form_valid(self, form):
        self.object = form.save()
        return render_to_response('yummy/cookbook/fill_success.html')

    def get(self, request, *args, **kwargs):
        try:
            CookBookRecipe.objects.get(recipe_id=kwargs['recipe_id'], cookbook__owner=request.user)
        except CookBookRecipe.DoesNotExist:
            return super(FavoriteRecipeAdd, self).get(request, *args, **kwargs)
        else:
            return render_to_response('yummy/cookbook/fill_exists.html')


class CookBookList(CynosureList):
    template_name = 'yummy/cookbook/list.html'

    def get_cynosure(self):
        return User.objects.get(pk=self.kwargs['user_id'])

    def get_queryset(self):
        qs = CookBook.objects.filter(owner=self.cynosure)
        if self.cynosure != self.request.user:
            qs = qs.filter(is_public=True)
        return qs


class CookBookDetail(CynosureList):
    template_name = 'yummy/cookbook/detail.html'

    def get_cynosure(self):
        return CookBook.objects.get(slug=self.kwargs['cookbook'], owner__pk=self.kwargs['user_id'])

    def get_queryset(self):
        if self.cynosure.owner != self.request.user:
            qs = Recipe.objects.public().filter(cookbook=self.cynosure)
        else:
            qs = Recipe.objects.filter(cookbook=self.cynosure)
        return qs


class CookBookPrint(CynosureList):

    template_name = 'yummy/cookbook/print.html'

    def get_cynosure(self):
        return CookBook.objects.get(slug=self.kwargs['cookbook'], owner__pk=self.kwargs['user_id'])

    def get_queryset(self):
        return Recipe.objects.filter(cookbookrecipe__cookbook=self.cynosure)


class CookBookMixin(SingleObjectTemplateResponseMixin):
    template_name = 'yummy/cookbook/new.html'
    model = CookBook
    form_class = CookBookAddForm

    def get_initial(self):
        return {
            'owner': self.request.user
        }


class CookBookAdd(CreateView, CookBookMixin):
    pass


class CookBookEdit(UpdateView, CookBookMixin):

    def get_object(self, queryset=None):
        return CookBook.objects.get(slug=self.kwargs['slug'], owner=self.request.user)


class CookBookRemove(DeleteView):

    def get_object(self, queryset=None):
        try:
            return CookBook.objects.get(slug=self.kwargs['slug'], owner=self.request.user)
        except CookBook.DoesNotExist:
            raise Http404(unicode(_("Given cookbook doesn't exists")))

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.object.is_default:
            return HttpResponseForbidden(unicode(_("Cannot delete default cookbook")))

        form = CookBookDeleteForm(data=request.POST, instance=self.object)
        if form.is_valid():
            self.object.delete()

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        user = self.request.user
        return reverse('yummy:cookbook_list', args=(slugify(user.username), user.pk,))


class FavoriteRecipeRemove(DeleteView):

    template_name = 'yummy/cookbook/recipe_remove.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseForbidden(_("This function is available to logged users only"))
        return super(FavoriteRecipeRemove, self).dispatch(request, *args, **kwargs)

    def form_invalid(self, form):
        return render_to_response('yummy/cookbook/recipe_remove_fail.html')

    def form_valid(self, form):
        object = self.get_object()
        object.delete()
        return render_to_response('yummy/cookbook/recipe_remove_success.html', {'object': object})

    def get_object(self, queryset=None):
        try:
            return CookBookRecipe.objects.get(recipe_id=self.kwargs['recipe_id'], cookbook__owner=self.request.user)
        except CookBookRecipe.DoesNotExist:
            raise Http404(unicode("Given recipe not found"))

    def post(self, request, *args, **kwargs):
        #dummy form to check CSRF
        form = forms.Form(data=request.POST)
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        data = super(FavoriteRecipeRemove, self).get_context_data(**kwargs)
        #dummy form to check CSRF
        data['form'] = forms.Form()
        return data


class FavoriteRecipeEdit(UpdateView):
    template_name = 'yummy/cookbook/recipe_edit.html'
    form_class = CookBookEditForm

    def get_object(self, queryset=None):
        try:
            return CookBookRecipe.objects.get(recipe__slug=self.kwargs['slug'],
                                              cookbook__slug=self.kwargs['cookbook_slug'],
                                              cookbook__owner=self.request.user)
        except CookBookRecipe.DoesNotExist:
            raise Http404(unicode("Given recipe not found"))

    def form_valid(self, form):
        self.object.note = form.cleaned_data['note']
        self.object.save()

        return HttpResponse(self.object.note)

    def form_invalid(self, form):
        self.object.note = form.cleaned_data['note']
        self.object.save()

        return HttpResponse(self.object.note)


class ShoppingListView(ListView):
    model = ShoppingList


class ShoppingListDetailView(DetailView):
    pass
