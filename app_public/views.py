from django.contrib.auth import logout
from django.conf import settings
from django.shortcuts import render_to_response
from django.contrib.auth import login
from app_public.models import Person, Account
from datetime import datetime
from decimal import *
from app_public.forms import SSCAJoinForm


def dashboard_main_page(request):
    return render_to_response('index.html')


def logout_page(request):
    """ Log users out and re-direct them to the main page. """
    logout(request)
    return HttpResponseRedirect('/')


def post_auth_process(request, backend, *args, **kwargs):
    """Post authentication process"""

    try:  # Get the identity from the response returned by the OpenId provider.
        openid_identity = request.REQUEST['openid.identity']
        print openid_identity

        try:  # Check whether an user exists with this Identity.
            person = Person.objects.get(identity=openid_identity)

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
                return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)

            else:  # If the subscription seems to be expired, ask the user to renew it.
                message = {
                    'title': 'Subscription Expired',
                    'description': 'Your subscription seems to be expired. Please renew it.'
        }

        except Person.DoesNotExist:
            # TODO: If an user with such identity not exists, register the new user
            # For now, just show the message that the user is not registered.
                message = {
                            'title': 'No registration found',
                            'description': 'You seem to be not registered. Please register with your details.'
                }

        except Account.DoesNotExist:
            # If the user has no subscription yet, ask him to subscribe.
            message = {
                        'title': 'No Subscription found',
                        'description': 'You seem to be not chosen any subscription. Please subscribe.'
            }

    except KeyError:  # Handle the case of no identity found in the Openid provider response.
        # Message to the user as error in authentication.
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
