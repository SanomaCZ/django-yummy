from haystack import indexes

from yummy.models import Recipe


class YummyRecipeIndex(object):
    """
    Extend this index like this::

        class RecipeIndex(YummyRecipeIndex, indexes.RealTimeSearchIndex, indexes.Indexable):

            rating = indexes.DecimalField(boost=3)
            tags = indexes.MultiValueField(faceted=True)

            def  prepare_rating(self, obj):
                ...

            def prepare_tags(self, obj):
                ...
    """

    title = indexes.CharField(model_attr='title', boost=5)
    category = indexes.CharField(model_attr='category', boost=2)
    cooking_type = indexes.CharField(model_attr='cooking_type', faceted=True)
    cuisines = indexes.MultiValueField(faceted=True)
    owner = indexes.CharField(model_attr='owner', faceted=True)
    ingredients = indexes.MultiValueField(faceted=True, boost=4)
    ingredient_groups = indexes.MultiValueField(faceted=True)
    consumers = indexes.MultiValueField(faceted=True)

    def prepare_category(self, obj):
        return obj.category.title

    def prepare_cuisines(self, obj):
        return [c.name for c in obj.cuisines.all()]

    def prepare_ingredients(self, obj):
        return [i.name for i in obj.ingredientinrecipe_set.all()]

    def prepare_ingredient_groups(self, obj):
        return [i.group.name for i in obj.ingredientinrecipe_set.all()]

    def prepare_consumers(self, obj):
        return [c.title for c in obj.consumers.all()]

    def get_model(self):
        return Recipe

    def index_set(self):
        return self.get_model().objects.approved()
