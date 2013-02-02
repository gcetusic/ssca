from django.contrib.auth import logout
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.contrib.auth import login
from app_public.models import Person, Account
from datetime import datetime
from app_public.models import Location
from app_public.forms import SSCAJoinForm
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from numpy import vstack
from Pycluster import kcluster, clustercentroids
from decimal import *
import json
from django.core import serializers


def dashboard_main_page(request):
    return render_to_response('index.html')


def logout_page(request):
    """ Log users out and re-direct them to the main page. """
    logout(request)
    return HttpResponseRedirect('/')

def post_auth_process(request, backend, *args, **kwargs):
    """Post authentication process"""

    try: # Get the identity from the response returned by the OpenId provider.
        openid_identity = request.REQUEST['openid.identity']
        print openid_identity

        try: # Check whether an user exists with this Identity.
            person = Person.objects.get(identity = openid_identity)

            # If exists, check whether the user has subscribed.
            account = Account.objects.get(user = person.user)

            # If subscribed, check whether the subscription is not expired.
            # If the subscription is not expired, login the user.
            current_date = datetime.now().date()
            if current_date >= account.subscription.start_date and \
               current_date <= account.subscription.end_date:
                user = person.user
                user.backend = 'social_auth.backends.google.GoogleBackend'
                login(request, person.user)
                return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)


            else: # If the subscription seems to be expired, ask the user to renew it.
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

    except KeyError: # Handle the case of no identity found in the Openid provider response.
        # Message to the user as error in authentication.
        message = {
            'title': 'Authentication Error',
            'description': 'There occurs error in authentication. Please try again.'
        }

    return render_to_response('error.html', {"message": message})


@csrf_exempt
def gmaps(request):
    context = {}

    if request.is_ajax and request.POST:
        coordinates = Location.objects.filter( \
            latitude__gte=float(request.POST['south']), \
            latitude__lte=float(request.POST['north']), \
            longitude__gte=float(request.POST['west']), \
            longitude__lte=float(request.POST['east']))
        markers = []
        cluster_number = 100
        if len(coordinates) >= cluster_number:
            locations = vstack(map(list, coordinates.values_list('latitude', 'longitude'))).astype('float')
            clustermap, _, _ = kcluster(locations, cluster_number)
            clusters, _ = clustercentroids(locations, clusterid=clustermap)
            for location in clusters:
                markers.append({
                    'position': ("%.1f" % location[0], "%.1f" % location[1]),
                    'title': "Hello World",
                    'is_cluster': True
                })
        else:
            locations = coordinates.values('id', 'latitude', 'longitude')
            for location in locations:
                markers.append({
                    'id': location['id'],
                    'position': ("%.1f" % location['latitude'], "%.1f" % location['longitude']),
                    'title': "Hello World",
                    'is_cluster': False
                })
        return HttpResponse(json.dumps(markers))
    else:
        google_map = {
            'center': (0, 0),
            'zoom': 2,
        }
        context['gmap'] = google_map
        context['google_maps_key'] = settings.GOOGLE_MAPS_KEY
    return render_to_response('map.html', RequestContext(request, context))


@csrf_exempt
def marker_info(request):
    if 'id' in request.POST:
        data = serializers.serialize("json", Location.objects.filter(id=request.POST['id']))
        return HttpResponse(data)

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
