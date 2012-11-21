from django import forms

from yummy.models import CookBookRecipe, CookBook


class FavoriteRecipeForm(forms.ModelForm):

    class Meta:
        model = CookBookRecipe
        fields = ('cookbook', 'note', 'recipe')


    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')

        super(FavoriteRecipeForm, self).__init__(*args, **kwargs)

        cookbooks = list(CookBook.objects.filter(owner=self.user))
        if not cookbooks:
            cookbooks = [CookBook.objects.create_default(user=self.user)[0]]

        self.fields['cookbook'].choices = [(one.pk, one.title) for one in cookbooks]

        self.fields['recipe'].widget = forms.HiddenInput()

    def clean(self):
        data = self.cleaned_data
        data['owner'] = self.user.pk

        return data
