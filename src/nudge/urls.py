from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^batch/$', 'nudge.views.batch'),
)