from yummy.models import Category
from django.conf import settings

def common(request):
    return {
        'BASE_TEMPLATE': getattr(settings, 'YUMMY_EXTENDS_TEMPLATE', 'base.html'),
        'recipes_categories': Category.objects.filter(parent__isnull=True),
    }
