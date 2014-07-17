from django.conf.urls import patterns, include

urlpatterns = patterns('',
    ('^', include('yummy.urls', namespace='yummy')),
)
