from django.conf.urls.defaults import patterns, include

urlpatterns = patterns('',
    ('^', include('yummy.urls', namespace='yummy')),
)
