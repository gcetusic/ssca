from django.contrib.auth import logout
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.contrib.auth import login
from app_public.models import Person, Account
from datetime import datetime
from app_public.models import Location
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from decimal import *
from clustering import distance
import json


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


def decimal_to_float(location, *args):
    for arg in args:
        location[arg] = float(location[arg])
    return location


@csrf_exempt
def gmaps(request):
    context = {}

    if request.is_ajax and request.POST:
        locations = Location.objects.filter( \
            latitude__gte=float(request.POST['south']), \
            latitude__lte=float(request.POST['north']), \
            longitude__gte=float(request.POST['west']), \
            longitude__lte=float(request.POST['east'])).values('id', 'latitude', 'longitude')

        markers = []
        locations = map(lambda x: decimal_to_float(x, 'latitude', 'longitude'), locations)
        clusters = distance.cluster(locations, 80, int(request.POST.get('zoom', 3)), 'latitude', 'longitude')

        for cluster in clusters:
            if len(cluster) > 1:
                centroid = distance.centroid(cluster, 'latitude', 'longitude')
                markers.append({
                    'position': ("%.3f" % centroid[0], "%.3f" % centroid[1]),
                    'is_cluster': True
                })
            else:
                location = cluster[0]
                markers.append({
                    'id': location['id'],
                    'position': ("%.3f" % location['latitude'], "%.3f" % location['longitude']),
                    'is_cluster': False
                })
        return HttpResponse(json.dumps(markers))

    else:
        google_map = {
            'center': (20, 0),
            'zoom': 3,
            'minzoom': 2
        }
        context['gmap'] = google_map
        context['google_maps_key'] = settings.GOOGLE_MAPS_KEY
    return render_to_response('map.html', RequestContext(request, context))


@csrf_exempt
def marker_info(request):
    if 'id' in request.POST:
        data = Location.objects.filter(id=request.POST['id'])
        info = {
            'person': data[0].person.user.username,
            'date': data[0].date.strftime("%Y-%m-%d"),
            'position': ("%.3f" % data[0].latitude, "%.3f" % data[0].longitude),
        }
        return HttpResponse(json.dumps(info))
