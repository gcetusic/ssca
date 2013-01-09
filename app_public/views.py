from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django import forms
from gmapi import maps
from gmapi.forms.widgets import GoogleMap
from app_public.models import Coordinates


def dashboard_main_page(request):
    return render_to_response('index.html')


def logout_page(request):
    """ Log users out and re-direct them to the main page. """
    logout(request)
    return HttpResponseRedirect('/')


class MapForm(forms.Form):
    map = forms.Field(widget=GoogleMap(attrs={'width': 510, 'height': 510}))


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

    locations = Coordinates.objects.all()

    markers = []
    for location in locations:
        markers.append(maps.Marker(opts={
            'map': gmap,
            'position': maps.LatLng(location.longitude, location.latitude),
        }))



    marker1 = maps.Marker(opts={
        'map': gmap,
        'position': maps.LatLng(38, 360),
    })

    marker2 = maps.Marker(opts={
        'map': gmap,
        'position': maps.LatLng(-50, 10000),
    })

    marker3 = maps.Marker(opts={
        'map': gmap,
        'position': maps.LatLng(0, 0),
    })

    context = {'form': MapForm(initial={'map': gmap, 'marker': markers})}
    return render_to_response('map.html', context)
