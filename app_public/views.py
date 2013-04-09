from django.contrib.auth import logout
from django.conf import settings
from django.shortcuts import render_to_response
from django.contrib.auth import login
from django.template import loader, RequestContext
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.core.urlresolvers import reverse
from django.core.xheaders import populate_xheaders
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_protect
from app_public.models import Person, Account, Page
from datetime import datetime
from decimal import *
import json
from app_public.forms import SSCAJoinForm


def dashboard_main_page(request):
    return render_to_response('index.html')


def logout_page(request):
    """ Log users out and re-direct them to the main page. """
    logout(request)
    return HttpResponseRedirect(reverse('public-page'))


def member_page(request):
    """
    View for members page.
    """
    return render_to_response('member.html', {}, RequestContext(request))


def post_auth_process(request, backend, *args, **kwargs):
    """Post authentication process"""

    try:  # Get the identity from the response returned by the OpenId provider.
        openid_identity = request.REQUEST['openid.identity']
        print "------> openid=", openid_identity

        try:  # Check whether an user exists with this Identity.
            person = Person.objects.get(identity=openid_identity)

            print "found person", person.__dict__

            # If exists, check whether the user has subscribed.
            account = Account.objects.get(user=person.user)

            # If subscribed, check whether the subscription is not expired.
            # If the subscription is not expired, login the user.
            current_date = datetime.now().date()
            if current_date >= account.subscription.start_date and \
               current_date <= account.subscription.end_date:
                user = person.user
                user.backend = 'social_auth.backends.google.GoogleBackend'
                login(request, person.user)
                print "---------------- Login Success redirect ----------------"
                return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)

            else:  # If the subscription seems to be expired, ask the user to renew it.
                print "---------------- Subscription Expired ----------------"
                message = {
                    'title': 'Subscription Expired',
                    'description': 'Your subscription seems to be expired. Please renew it.'
                }

        except Person.DoesNotExist:
            print "---------------- PersonDoesNotExist ----------------"
            context = {"error_type": "PersonDoesNotExist"}
            return render_to_response('public.html', RequestContext(request, context))

        except Account.DoesNotExist:
            print "-- Account DoesNotExist --"
            # If the user has no subscription yet, ask him to subscribe.
            message = {
                        'title': 'No Subscription found',
                        'description': 'You seem to be not chosen any subscription. Please subscribe.'
            }

    except KeyError:  # Handle the case of no identity found in the Openid provider response.
        # Message to the user as error in authentication.
        print "------> KeyError"
        message = {
            'title': 'Authentication Error',
            'description': 'There occurs error in authentication. Please try again.'
        }

    return render_to_response('error.html', {"message": message})


def join(request):
    """
    Function handles join popups. join form is shown if user has
    not already joined.

    :param request: django HttpRequest

    :return: django HttpResponse
    """
    #assuming new user
    user_exist = False
    form = SSCAJoinForm()
    c = {'form': form, 'basic_mail_cost': 55}
    return render_to_response('join.html', c)


def renew(request):
    """
    Function handles renew popups.

    :param request: django HttpRequest

    :return: django HttpResponse
    """
    return render_to_response('renew.html')


def public_page(request):
    #assuming new user
    user_exist = False
    form = SSCAJoinForm()
    c = {'form': form, 'basic_mail_cost': 55}
    return render_to_response('public.html', c, context_instance=RequestContext(request))


def dajax_test(request):
    """test view to evaluate dajax capabilities"""
    return render_to_response('dajax-test.html')


DEFAULT_TEMPLATE = 'flatpages/default.html'


@csrf_protect
def render_page(request, f):
    """
    Internal interface to the flat page view.
    """
    if f.template_name:
        t = loader.select_template((f.template_name, DEFAULT_TEMPLATE))
    else:
        t = loader.get_template(DEFAULT_TEMPLATE)

    # To avoid having to always use the "|safe" filter in flatpage templates,
    # mark the title and content as already safe (since they are raw HTML
    # content in the first place).
    f.title = mark_safe(f.title)
    f.content = mark_safe(f.content)

    picture = None
    if f.picture.exists():
        picture = mark_safe(f.picture.order_by('?')[0].render())

    c = RequestContext(request, {
        'page': f,
        'picture': picture
    })

    response = HttpResponse(t.render(c))
    populate_xheaders(request, response, Page, f.id)
    return response


def render_page_ajax(request, f):
    # To avoid having to always use the "|safe" filter in flatpage templates,
    # mark the title and content as already safe (since they are raw HTML
    # content in the first place).
    f.title = mark_safe(f.title)
    f.content = mark_safe(f.content)

    picture = None
    if f.picture.exists():
        picture = mark_safe(f.picture.order_by('?')[0].render())

    response = json.dumps({
        'title': f.title,
        'content': f.content,
        'picture': picture
    })

    return response


def sscapage(request, url):
    """
    Public interface to the page view.

    Models: `models.page`
    Templates: Uses the template defined by the ``template_name`` field,
        or `flatpages/default.html` if template_name is not defined.
    Context:
        flatpage
            `flatpages.flatpages` object
    """

    if not url.startswith('/'):
        url = '/' + url
    try:
        f = get_object_or_404(Page, url__exact=url, sites__id__exact=settings.SITE_ID)
    except Http404:
        if not url.endswith('/') and settings.APPEND_SLASH:
            url += '/'
            f = get_object_or_404(Page, url__exact=url, sites__id__exact=settings.SITE_ID)
            return HttpResponsePermanentRedirect('%s/' % request.path)
        else:
            raise

    # If registration is required for accessing this page, and the user isn't
    # logged in, redirect to the login page.
    if f.registration_required and not request.user.is_authenticated():
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(request.path)

    if request.is_ajax():
        return render_page_ajax(request, f)
    else:
        return render_page(request, f)
