from django.conf.urls.defaults import *
from app_backoffice.views import *

urlpatterns = patterns('',
    # Admin backoffice pages.
    (r'^$', backoffice_main_page),
    url(r'^grid/$', grid_handler, name='grid_handler'),
    url(r'^grid/cfg/$', grid_config, name='grid_config'),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
                                  {'document_root': 'static'}),
)

