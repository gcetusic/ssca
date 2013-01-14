from django.contrib.auth import logout
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from app_public.models import Coordinates
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
        data = serializers.serialize("json", Coordinates.objects.filter(id=request.POST['id']))
        return HttpResponse(data)
