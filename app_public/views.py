from django.contrib.auth import logout
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from app_public.models import Coordinates
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from numpy import vstack
from scipy.cluster.vq import kmeans, vq
from math import sqrt
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
        print len(coordinates)
        cluster_number = 200
        locations = vstack(map(list, coordinates.values_list('latitude', 'longitude'))).astype('float')
        if len(coordinates) >= cluster_number:
            clusters, _ = kmeans(locations, cluster_number)
            is_cluster = True
        else:
            clusters = locations
            is_cluster = False

        idx, _ = vq(locations, clusters)
        markers = []
        for location in clusters:
            markers.append({
                'position': ("%.1f" % location[0], "%.1f" % location[1]),
                'title': "Hello World",
                'is_cluster': is_cluster
            })
        print len(markers)
        return HttpResponse(json.dumps(markers))
    else:
        google_map = {
            'center': (0, 0),
            'zoom': 4,
        }
        context['gmap'] = google_map
    return render_to_response('map.html', RequestContext(request, context))
