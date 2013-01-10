from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django import forms
from gmapi import maps
from gmapi.forms.widgets import GoogleMap
from app_public.models import Coordinates
from math import sqrt, pi, log
import itertools
from decimal import *
from numpy import vstack, array
from scipy.cluster.vq import kmeans,vq
import random


def dashboard_main_page(request):
    return render_to_response('index.html')


def logout_page(request):
    """ Log users out and re-direct them to the main page. """
    logout(request)
    return HttpResponseRedirect('/')


class MapForm(forms.Form):
    map = forms.Field(widget=GoogleMap(attrs={'width': 510, 'height': 510}))


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


def gmaps(request):
    gmap = maps.Map(
        opts={
            'center': maps.LatLng(38, -97),
            'mapTypeId': maps.MapTypeId.ROADMAP,
            'zoom': 3,
            'mapTypeControlOptions': {
                'style': maps.MapTypeControlStyle.DROPDOWN_MENU
            },
        }
    )

    locations1 = Coordinates.objects.all()
    locations = vstack(map(list, Coordinates.objects.values_list('latitude', 'longitude'))).astype('float')
    clusters, _ = kmeans(locations, sqrt(len(locations) / 2))
    idx, _ = vq(locations, clusters)

    # for pair in itertools.product(locations, repeat=2):
    #     print cluster_locations(*pair)

    markers = []
    for location in locations1:
        markers.append(maps.Marker(opts={
            'map': gmap,
            'position': maps.LatLng(location.latitude, location.longitude),
        }))

    context = {'form': MapForm(initial={'map': gmap, 'marker': markers})}
    return render_to_response('map.html', context)
