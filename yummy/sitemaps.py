from django.contrib.sitemaps import Sitemap

from yummy.models import Recipe, Category, Ingredient

class RecipeSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Recipe.objects.public()

    def lastmod(self, obj):
        return obj.updated


class RecipeCategorySitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        return Category.objects.all()


class IngredientSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        return Ingredient.objects.approved()
