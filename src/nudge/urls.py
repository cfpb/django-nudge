from django.conf.urls import patterns, url


urlpatterns = patterns('nudge.views',
                       url(r'^batch/$', 'batch'),
                       url(r'^check-versions/$', 'check_versions'),)
