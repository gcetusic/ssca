from django.contrib.auth import logout
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from app_public.models import Coordinates
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from numpy import vstack
from scipy.cluster.vq import kmeans
from decimal import *
import json


def dashboard_main_page(request):
    return render_to_response('index.html')


def logout_page(request):
    """ Log users out and re-direct them to the main page. """
    logout(request)
    return HttpResponseRedirect('/')


@csrf_exempt
def gmaps(request):
    context = {}

    if request.is_ajax and request.POST:
        coordinates = Coordinates.objects.filter( \
            latitude__gte=float(request.POST['south']), \
            latitude__lte=float(request.POST['north']), \
            longitude__gte=float(request.POST['west']), \
            longitude__lte=float(request.POST['east']))
        markers = []
        cluster_number = 200
        if len(coordinates) >= cluster_number:
            locations = vstack(map(list, coordinates.values_list('latitude', 'longitude'))).astype('float')
            clusters, _ = kmeans(locations, cluster_number)
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
            'zoom': 4,
        }
        context['gmap'] = google_map
        context['google_maps_key'] = settings.GOOGLE_MAPS_KEY
    return render_to_response('map.html', RequestContext(request, context))


def marker_info(request, marker_id=None):
    if marker_id:
        coordinates = Coordinates.objects.filter(id=marker_id)
        return HttpResponse(json.dumps(coordinates))
