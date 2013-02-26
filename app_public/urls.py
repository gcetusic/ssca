from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings
from app_public.views import *

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'django.views.generic.simple.direct_to_template', {'template': 'index.html'}),
    url(r'^login/$', 'django.contrib.auth.views.login'),
    url(r'^logout/$', logout_page),
    url(r'^dashboard/', include('app_dashboard.urls')),
    #url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
                                  #{'document_root': 'static'}),
    url(r'^admin/', include(admin.site.urls)),

    # Overriding Social Auth to implement a custom Post Auth logic.
    url(r'^accounts/complete/(?P<backend>[^/]+)/$', post_auth_process,
        name='socialauth_complete'),

    # Social Auth URLs
    url(r'^accounts/', include('social_auth.urls')),

    # Join
    url(r'^join/', join),

    # Renew
    url(r'^renew/', renew),

    url(r'^', include('cms.urls')),
)

if settings.DEBUG:
    urlpatterns = patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
        url(r'', include('django.contrib.staticfiles.urls')),
    ) + urlpatterns
