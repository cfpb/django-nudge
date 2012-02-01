from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    url(r'batch/$', 'nudge.views.batch'),
)