from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.conf import settings
from django.db.models import Q
from django.core import serializers
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
from django.utils.timezone import activate, get_current_timezone_name
from itertools import chain
from app_dashboard.models import Location, Port, CruisingStation, Guide
from clustering import distance
import json

CLUSTERING_ALGORITHMS = [
    'qt', # helpers.cluster_qt - largest cluster first
    'smart', # helpers.cluster_smart - Precalculate some constants outside the loop
    'naive', # helpers.cluster_naive - sequential search
    'old', # distance.cluster - old one    
]
DEFAULT_CLUSTERING_ALGORITHM = getattr(settings, 'DEFAULT_CLUSTERING_ALGORITHM', CLUSTERING_ALGORITHMS[0])


@login_required
def dashboard_main_page(request):
    """ 
    If users are authenticated, direct them to the main page. Otherwise,
    take them to the login page. 
    """
    context = {}
    # Initial configuration for Google Maps
    google_map = {
        'center': (20, 0),
        'zoom': 2,
        'minzoom': 2
    }
    context['gmap'] = google_map
    context['google_maps_key'] = settings.GOOGLE_MAPS_KEY

    return render_to_response('dashboard/index.html', context, RequestContext(request))


@login_required
def dashboard_map_ajax(request):
    """
    Contains HTML contents of MAP page
    """
    return render_to_response('dashboard/ajax/map.html', {}, RequestContext(request))


@csrf_exempt
def show_gmaps(request):
    context = {}
    if request.is_ajax() and request.method == "POST":

        # Set the timezone to the client's or server's if none specified
        timezone = request.POST.get('timezone', get_current_timezone_name())
        zoom = int(request.POST.get('zoom', 3))        
        activate(timezone)
        if settings.DEBUG:
            clustering = request.POST.get('clustering', DEFAULT_CLUSTERING_ALGORITHM)        
        else:
            clustering = DEFAULT_CLUSTERING_ALGORITHM        

        # Get all markers in the last x minutes
        deltatime = int(request.POST.get('time', 0))

        # Get the ids of recent locations, or latest if change parameter is 0
        location_ids = Location.objects.current_location(change=deltatime)
        locations = Location.objects.filter(
            latitude__gte=float(request.POST['south']),
            latitude__lte=float(request.POST['north']),
            longitude__gte=float(request.POST['west']),
            longitude__lte=float(request.POST['east']),
            id__in=location_ids).values('id', 'latitude', 'longitude')

        for location in locations:
            location['category'] = 'members'

        ports = Port.objects.filter(
            latitude__gte=float(request.POST['south']),
            latitude__lte=float(request.POST['north']),
            longitude__gte=float(request.POST['west']),
            longitude__lte=float(request.POST['east'])).values('id', 'latitude', 'longitude')

        for port in ports:
            port['category'] = 'guides'

        stations = CruisingStation.objects.filter(
            latitude__gte=float(request.POST['south']),
            latitude__lte=float(request.POST['north']),
            longitude__gte=float(request.POST['west']),
            longitude__lte=float(request.POST['east'])).values('id', 'latitude', 'longitude')

        for station in stations:
            station['category'] = 'stations'

        markers = []

        result_list = list(chain(locations, ports, stations))
        result_list = map(lambda x: Location().decimal_to_float(x, 'latitude', 'longitude'), result_list)
        
        # Clustering algorithm selection
        clusters = distance.smart_cluster(result_list, 80, zoom, clustering, 'latitude', 'longitude')

        for center, cluster in clusters:
            cluster_count = len(cluster)
            if cluster_count > 1:
                category = 'cluster'                
                markers.append({
                    'position': ("%.3f" % center[0], "%.3f" % center[1]),
                    'category': "cluster",
                    'count': cluster_count,
                })
            else:
                location = cluster[0]
                category = location['category']
                markers.append({
                    'id': location['id'],
                    'position': ("%.3f" % location['latitude'], "%.3f" % location['longitude']),
                    'category': category,
                })    
        return HttpResponse(json.dumps(markers))

    else:
        google_map = {
            'center': (20, 0),
            'zoom': 2,
            'minzoom': 2
        }
        context['gmap'] = google_map
        context['google_maps_key'] = settings.GOOGLE_MAPS_KEY
        if settings.DEBUG:
            context['clustering'] = request.GET.get('clustering', DEFAULT_CLUSTERING_ALGORITHM)
        else:
            context['clustering'] = DEFAULT_CLUSTERING_ALGORITHM                   
    return render_to_response('map.html', RequestContext(request, context))


@csrf_exempt
def marker_info(request):
    if 'id' in request.POST:
        if 'category' in request.POST:
            category = request.POST.get('category')
            if category == 'members':
                data = Location.objects.get(id=request.POST['id'])
            elif category == 'guides':
                data = Guide.objects.filter(port__id=request.POST['id']).latest('date')
            elif category == 'stations':
                data = CruisingStation.objects.get(id=request.POST['id'])
        else:
            data = Location.objects.get(id=request.POST['id'])

        timezone = request.POST.get('timezone', get_current_timezone_name())
        activate(timezone)

        info = data.get_info()
        return HttpResponse(json.dumps(info))


class MemberSearch(object):
    def __init__(self, search_data):
        self.__dict__.update(search_data)

    def search_email(self, q=None):
        email_q = Q(email__icontains=self.search)
        if q is not None:
            q |= email_q
        else:
            q = email_q
        return q

    def search_first_name(self, q=None):
        first_name_q = Q(first_name__icontains=self.search)
        if q is not None:
            q |= first_name_q
        else:
            q = first_name_q
        return q

    def search_last_name(self, q=None):
        last_name_q = Q(last_name__icontains=self.search)
        if q is not None:
            q |= last_name_q
        else:
            q = last_name_q
        return q


@csrf_exempt
def find_member(request):
    if 'search' in request.POST:
        timezone = request.POST.get('timezone', get_current_timezone_name())
        activate(timezone)

        results = None
        searcher = MemberSearch({'search': request.POST.get('search')})

        q = None
        for key in ("email", "first_name", "last_name"):
            dispatch = getattr(searcher, 'search_%s' % key)
            q = dispatch(q)

        if q and len(q):
            user_ids = User.objects.filter(q).values_list('id', flat=True)

            location_ids = Location.objects.current_location(change=0, user_ids=user_ids)
            locations = Location.objects.filter(id__in=location_ids)

            results = serializers.serialize('json', locations,
                excludes=('date'), fields=('latitude', 'longitude', 'person'),
                relations={'person': {'excludes': ('identity', 'friend',),
                'relations': {'user': {'excludes':
                ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions',
                 'password', 'last_login', 'date_joined')
                }}}})

        return HttpResponse(results)

def dashboard_test_mockup(request):
    """ test view for dashboard mockup """
    return render_to_response('dashboard/index.html', {}, RequestContext(request))
