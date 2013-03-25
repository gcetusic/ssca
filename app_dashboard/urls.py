from django.conf.urls.defaults import *
from app_dashboard.views import *

urlpatterns = patterns('',
    # Main web portal entrance.
    (r'^test_mockup/$', dashboard_test_mockup),
    (r'^$', dashboard_main_page),
)
