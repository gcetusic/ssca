from app_public.views import sscapage
from django.http import Http404
from django.conf import settings


class SSCAPageMiddleware(object):
    def process_response(self, request, response):
        if response.status_code != 404:
            return response
        try:
            return sscapage(request, request.path_info)
        # Return the original response if any errors happened. Because this
        # is a middleware, we can't assume the errors will be caught elsewhere.
        except Http404:
            return response
        except:
            if settings.DEBUG:
                raise
            return response
