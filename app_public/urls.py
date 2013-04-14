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
    url(r'^$', public_page, name='public-page'),
    url(r'^register/$', register_page),

    # token must be [a-zA-Z0-1] and 64 chars in length, incase token length in
    # url does not match the registration page will not be shown
    url(r'^registration/complete/(?P<token>[a-zA-Z0-9]{64})$', registration_complete),

    url(r'^base/$', 'django.views.generic.simple.direct_to_template', {'template': 'base.html'}),
    url(r'^public/$', public_page),
    url(r'^member/$', member_page, name="member-page"),
    url(r'^login/$', 'django.contrib.auth.views.login'),
    url(r'^logout/$', logout_page, name='logout'),
    url(r'^dashboard/', include('app_dashboard.urls')),
    url(r'^backoffice/', include('app_backoffice.urls')),
    url(r"^search/", include("watson.urls", namespace="watson")),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
                                  {'document_root': 'static'}),
    url(r'^admin/', include(admin.site.urls)),

    # Overriding Social Auth to implement a custom Post Auth logic.
    url(r'^accounts/complete/(?P<backend>[^/]+)/$', post_auth_process,
        name='socialauth_complete'),

    # Social Auth URLs
    url(r'^accounts/', include('social_auth.urls')),

    ('^pages/', include('django.contrib.flatpages.urls')),

    url(r'^location/', 'django.views.generic.simple.direct_to_template', {'template': 'location.html'})
)

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    urlpatterns = patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
        url(r'', include('django.contrib.staticfiles.urls')),
    ) + urlpatterns
