from django.conf.urls.defaults import *
from app_backoffice.views import *

urlpatterns = patterns('',
    # Admin backoffice pages.
    (r'^$', backoffice_main_page),

    url(r'^grid/$', grid_handler, name='grid_handler'),
    url(r'^grid/cfg/$', grid_config, name='grid_config'),
    url(r'^download_excel/$', download_excel, name='download_excel'),
    
    url(r'^acc_grid/$', acc_grid_handler, name='acc_grid_handler'),
    url(r'^acc_grid/cfg/$', acc_grid_config, name='acc_grid_config'),
    url(r'^acc_download_excel/$', acc_download_excel, name='acc_download_excel'),
    
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
                                  {'document_root': 'static'}),
)

