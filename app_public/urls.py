from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from app_public.views import *
from dajaxice.core import dajaxice_autodiscover, dajaxice_config

dajaxice_autodiscover()

admin.autodiscover()

urlpatterns = patterns('',

    # dajaxice urls
    url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),

    # test dajax page
    url(r'^dajax_test/', dajax_test),

    # url(r'^$', 'django.views.generic.simple.direct_to_template', {'template': 'index.html'}),
    url(r'^$', public_page),
    url(r'^base/$', 'django.views.generic.simple.direct_to_template', {'template': 'base.html'}),
    url(r'^public/$', public_page),
    url(r'^member/$', 'django.views.generic.simple.direct_to_template', {'template': 'member.html'}),
    url(r'^login/$', 'django.contrib.auth.views.login'),
    url(r'^logout/$', logout_page),
    url(r'^dashboard/', include('app_dashboard.urls')),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
                                  {'document_root': 'static'}),
    url(r'^admin/', include(admin.site.urls)),

    # Overriding Social Auth to implement a custom Post Auth logic.
    url(r'^accounts/complete/(?P<backend>[^/]+)/$', post_auth_process,
        name='socialauth_complete'),

    # Social Auth URLs
    url(r'^accounts/', include('social_auth.urls')),

    ('^pages/', include('django.contrib.flatpages.urls')),
)

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    urlpatterns = patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
        url(r'', include('django.contrib.staticfiles.urls')),
    ) + urlpatterns
