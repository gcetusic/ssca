import json
from dajaxice.decorators import dajaxice_register
from app_dashboard.views import show_gmaps
from app_public.views import sscapage
import re


@dajaxice_register(method='GET')
@dajaxice_register(method='POST', name='other_post')
def hello(request):
    print "-- hello --"
    return json.dumps({'message': 'hello'})


@dajaxice_register(method='GET')
@dajaxice_register(method='POST', name="more.complex.bye")
def bye(request):
    print "-- bye --"
    raise Exception("PUMMMM")
    return json.dumps({'message': 'bye'})


@dajaxice_register
def lol(request):
    print "-- lol --"
    return json.dumps({'message': 'lol'})


@dajaxice_register(method='GET')
def get_args(request, foo):
    print "-- owner --"
    return json.dumps({'message': 'hello get args %s' % foo})


@dajaxice_register(method='GET')
def get_public(request, id):
    pass


@dajaxice_register(method='GET')
def sscapage_ajax(request, page=None):
    return sscapage(request, page)

@dajaxice_register(method='GET')
def validate_location(request,location=None):
    if location is None:
        return json.dumps({'status': 'error'})
    pattern = re.compile('^[N|S|n|s](\d{2}) (\d{2}.\d{2}), [W|E|w|e](\d{3}) (\d{2}.\d{2})$')
    m = pattern.match(location)
    if m is not None:
        latitude_deg = int(m.groups(0)[0])
        latitude_min = float(m.groups(0)[1])
        longitude_deg = int(m.groups(0)[2])
        longitude_min = float(m.groups(0)[3])
        if 0 < latitude_deg < 90 and 0 < latitude_min < 60 and 0 < longitude_deg < 180 and 0 < longitude_min < 60:
            return json.dumps({'status': 'success'})
    return json.dumps({'status': 'error'})

