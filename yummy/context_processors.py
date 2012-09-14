from yummy.models import Category


def common(request):
    return {
        'recipes_categories': Category.objects.filter(parent__isnull=True),
    }
