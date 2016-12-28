from django import forms
from django.template.defaultfilters import slugify
from django.utils.html import strip_tags, escape
from django.utils.translation import ugettext_lazy as _

from yummy.models import (
    CookBookRecipe,
    CookBook,
    Ingredient,
    SubstituteIngredient
)


class FavoriteRecipeForm(forms.ModelForm):

    class Meta:
        model = CookBookRecipe
        fields = ('cookbook', 'note', 'recipe',)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')

        super(FavoriteRecipeForm, self).__init__(*args, **kwargs)

        cookbooks = list(CookBook.objects.filter(owner=self.user))
        if not cookbooks:
            cookbooks = [CookBook.objects.create_default(user=self.user)[0]]

        self.fields['cookbook'].choices = [(one.pk, one.title) for one in cookbooks]

        self.fields['recipe'].widget = forms.HiddenInput()
        self.fields['note'].widget = forms.Textarea()

    def clean(self):
        data = self.cleaned_data
        data['owner'] = self.user.pk

        return data


class CookBookAddForm(forms.ModelForm):

    class Meta:
        model = CookBook
        fields = ('id', 'title', 'is_public', 'owner',)

    def __init__(self, *args, **kwargs):
        super(CookBookAddForm, self).__init__(*args, **kwargs)
        self.fields['owner'].widget = forms.HiddenInput()

    def clean(self):
        data = self.cleaned_data

        qs = CookBook.objects.filter(slug=slugify(data['title']), owner=data['owner'])
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.count():
            raise forms.ValidationError(_("Cookbook with given title already exists"))

        return data


class CookBookDeleteForm(forms.ModelForm):

    class Meta:
        model = CookBook
        fields = ('id',)


class CookBookEditForm(forms.ModelForm):

    class Meta:
        model = CookBookRecipe
        fields = ('note',)

    def __init__(self, *args, **kwargs):
        super(CookBookEditForm, self).__init__(*args, **kwargs)
        self.fields['note'].widget = forms.Textarea()

    def clean_note(self):
        data = self.cleaned_data
        return escape(strip_tags(data['note']))


class SubstituteIngredientAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SubstituteIngredientAdminForm, self).__init__(*args, **kwargs)
        self.fields['substitute'].queryset = Ingredient.objects.approved()

    class Meta:
        fields = '__all__'
        model = SubstituteIngredient
