from django.conf.urls.defaults import *
from app_dashboard.views import *

urlpatterns = patterns('',
    # Main web portal entrance.
    (r'^$', dashboard_main_page),
    url(r'^marker/$', marker_info, name="marker_info"),
    url(r'^map/$', show_gmaps, name="gmaps_viewer"),
    url(r'^search/$', find_member, name="member_finder"),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
                                  {'document_root': 'static'}),
)

if settings.DEBUG:
    urlpatterns = patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
        url(r'', include('django.contrib.staticfiles.urls')),
    ) + urlpatterns
