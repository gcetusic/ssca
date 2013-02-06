from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
from django.utils.timezone import activate, get_current_timezone_name
from itertools import chain
from datetime import timedelta
from app_dashboard.models import Location, Port, CruisingStation
from clustering import distance
import json


@login_required
def dashboard_main_page(request):
    """ If users are authenticated, direct them to the main page. Otherwise,
        take them to the login page. """
    return render_to_response('dashboard/index.html')


@csrf_exempt
def gmaps(request):
    context = {}

    if request.is_ajax and request.POST:
        locations = Location.objects.filter( \
            latitude__gte=float(request.POST['south']), \
            latitude__lte=float(request.POST['north']), \
            longitude__gte=float(request.POST['west']), \
            longitude__lte=float(request.POST['east'])).values('id', 'latitude', 'longitude')

        ports = Port.objects.filter( \
            latitude__gte=float(request.POST['south']), \
            latitude__lte=float(request.POST['north']), \
            longitude__gte=float(request.POST['west']), \
            longitude__lte=float(request.POST['east'])).values('id', 'latitude', 'longitude')

        stations = CruisingStation.objects.filter( \
            latitude__gte=float(request.POST['south']), \
            latitude__lte=float(request.POST['north']), \
            longitude__gte=float(request.POST['west']), \
            longitude__lte=float(request.POST['east'])).values('id', 'latitude', 'longitude')

        markers = []

        result_list = list(chain(locations, ports, stations))
        result_list = map(lambda x: Location().decimal_to_float(x, 'latitude', 'longitude'), result_list)
        clusters = distance.cluster(result_list, 80, int(request.POST.get('zoom', 3)), 'latitude', 'longitude')

        for cluster in clusters:
            if len(cluster) > 1:
                centroid = distance.centroid(cluster, 'latitude', 'longitude')
                markers.append({
                    'position': ("%.3f" % centroid[0], "%.3f" % centroid[1]),
                    'is_cluster': True,
                    'category': "cluster"
                })
            else:
                location = cluster[0]
                markers.append({
                    'id': location['id'],
                    'position': ("%.3f" % location['latitude'], "%.3f" % location['longitude']),
                    'is_cluster': False,
                    'category': "members"
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
        if 'category' in request.POST:
            category = request.POST.get('category')
            if category == 'members':
                data = Location.objects.get(id=request.POST['id'])
            elif category == 'guides':
                data = Port.objects.get(id=request.POST['id'])
            elif category == 'stations':
                data = CruisingStation.objects.get(id=request.POST['id'])
        else:
            data = Location.objects.get(id=request.POST['id'])

        timezone = request.POST.get('timezone', get_current_timezone_name())
        activate(timezone)

        info = data.get_info()
        return HttpResponse(json.dumps(info))
