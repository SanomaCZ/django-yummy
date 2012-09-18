from haystack import indexes

from yummy.models import Recipe


class YummyRecipeIndex(indexes.RealTimeSearchIndex):
    """
    Extend this index like this::

        class RecipeIndex(YummyRecipeIndex, indexes.Indexable):

            rating = indexes.DecimalField(boost=3)
            tags = indexes.MultiValueField(faceted=True)

            def  prepare_rating(self, obj):
                ...

            def prepare_tags(self, obj):
                ...
    """

    title = indexes.CharField(model_attr='title', boost=5)
    description = indexes.CharField(model_attr='description', null=True)
    category = indexes.CharField(model_attr='category', boost=2)
    cooking_type = indexes.CharField(model_attr='cooking_type', null=True, faceted=True)
    cuisines = indexes.MultiValueField(faceted=True)
    owner = indexes.CharField(model_attr='owner', faceted=True)
    ingredients = indexes.MultiValueField(faceted=True, boost=4)
    ingredient_groups = indexes.MultiValueField(faceted=True)
    consumers = indexes.MultiValueField(faceted=True)
    servings = indexes.IntegerField(model_attr='servings', null=True)
    price = indexes.CharField(model_attr='get_price_display', faceted=True)
    difficulty = indexes.CharField(model_attr='get_difficulty_display', faceted=True)
    created = indexes.DateTimeField(model_attr='created')
    updated = indexes.DateTimeField(model_attr='updated')

    def prepare_category(self, obj):
        return obj.category.title

    def prepare_cuisines(self, obj):
        return [c.name for c in obj.cuisines.all()]

    def prepare_ingredients(self, obj):
        i_set = set()
        for i in obj.ingredientinrecipe_set.all():
            i_set.add(i.ingredient.name)
        return tuple(i_set)

    def prepare_ingredient_groups(self, obj):
        g_set = set()
        for i in obj.ingredientinrecipe_set.all():
            g_set.add(i.ingredient.group.name)
        return tuple(g_set)

    def prepare_consumers(self, obj):
        return [c.title for c in obj.consumers.all()]

    def get_model(self):
        return Recipe

    def index_set(self):
        return self.get_model().objects.public()
