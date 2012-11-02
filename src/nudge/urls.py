from django.conf.urls.defaults import *

urlpatterns = patterns('nudge.views',
    url(r'^batch/$', 'batch'),
    url(r'^check-versions/$', 'check_versions'),
)
