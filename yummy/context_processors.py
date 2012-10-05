from django.conf import settings

def common(request):
    return {
        'BASE_TEMPLATE': getattr(settings, 'YUMMY_BASE_TEMPLATE', 'base.html')
    }
