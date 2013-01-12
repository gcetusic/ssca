from django.contrib.auth import logout
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from app_public.models import Coordinates
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from numpy import vstack
from scipy.cluster.vq import kmeans, vq
from math import sqrt, pi, log
from decimal import *
import json


def dashboard_main_page(request):
    return render_to_response('index.html')


def logout_page(request):
    """ Log users out and re-direct them to the main page. """
    logout(request)
    return HttpResponseRedirect('/')


def pixel_distance(lat1, lon1, lat2, lon2, zoom):
    offset = 268435456
    radius = 85445659.4471
    lat1 = float(lat1)
    lon1 = float(lon1)
    lat2 = float(lat2)
    lon2 = float(lon2)

    x1 = round(offset + radius * lon1 * pi / 180)
    y1 = round(offset - radius *
                log((1 + sin(lat1 * pi / 180)) /
                (1 - sin(lat1 * pi / 180))) / 2)

    x2 = round(offset + radius * lon2 * pi / 180)
    y2 = round(offset - radius *
                log((1 + sin(lat2 * pi / 180)) /
                (1 - sin(lat2 * pi / 180))) / 2)

    return sqrt(pow((x1 - x2), 2) + pow((y1 - y2), 2)) / pow(21 - float(zoom), 2)


def cluster_locations(locations):
    clustered = []
    while locations:
        location = locations.pop()
        cluster = []
        for location in locations:
            pixels = pixel_distance(location1.latitude, location1.longitude, location2.latitude, location2.longitude, 3)

    return pixel_distance(location1.latitude, location1.longitude, location2.latitude, location2.longitude, 3)


@csrf_exempt
def gmaps(request):
    context = {}
    if request.is_ajax and request.POST:
        coordinates = Coordinates.objects.filter(latitude__gte=float(request.POST['south']), latitude__lte=float(request.POST['north']), longitude__gte=float(request.POST['west']), longitude__lte=float(request.POST['east']))

        locations = vstack(map(list, coordinates.values_list('latitude', 'longitude'))).astype('float')
        clusters, _ = kmeans(locations, sqrt(len(locations) / 2))
        idx, _ = vq(locations, clusters)

        markers = []
        for location in clusters:
            markers.append({
                'position': ("%.1f" % location[0], "%.1f" % location[1]),
                'title': "Hello World"
            })

        return HttpResponse(json.dumps(markers))
    else:
        google_map = {
            'center': (0, 0),
            'zoom': 6,
        }
        context['gmap'] = google_map
    return render_to_response('map.html', RequestContext(request, context))
