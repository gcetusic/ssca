from django.db import models
from django.utils import timezone
from django.utils.timezone import get_current_timezone

from app_public.models import Person
import math


class LocationManager(models.Manager):
    def current_location(self, change=None):
        '''
            The method takes a timedelta object as the 'change' argument.
            E.g. to get all locations that were edited in the last 30 minutes and id of 4:

            Location.objects.current_location(timezone.now() - timedelta(minutes=30)).filter(id=4)
        '''
        if change:
            date = super(LocationManager, self).get_query_set().filter( \
                date__gte=(timezone.now() - change) \
                )
        else:
            date = super(LocationManager, self).get_query_set().annotate(models.Max('date'))
        return date


class Location(models.Model):
    date = models.DateTimeField()
    latitude = models.DecimalField(max_digits=7, decimal_places=5)
    longitude = models.DecimalField(max_digits=8, decimal_places=5)
    person = models.ForeignKey(Person, blank=True, null=True)

    objects = LocationManager()

    def decimal_to_float(self, location, *args):
        for arg in args:
            location[arg] = float(location[arg])
        return location

    def format_coordinates(self, coordinate):
        minutes, degrees = math.modf(round(coordinate, 4))
        degrees = "%d" % degrees
        minutes = "%.2f" % round(minutes * 60, 2)
        return degrees + " " + minutes

    def get_info(self):
        usertime = self.date.astimezone(get_current_timezone())

        if self.latitude >= 0:
            latitude = "N" + " " + Location().format_coordinates(self.latitude)
        else:
            latitude = "S" + " " + Location().format_coordinates(self.latitude)

        if self.longitude >= 0:
            longitude = "E" + " " + Location().format_coordinates(self.longitude)
        else:
            longitude = "W" + " " + Location().format_coordinates(self.longitude)

        info = {
            'name': self.person.user.username,
            'date': usertime.strftime("%Y-%m-%d %H:%m"),
            'position': ("%s" % latitude, "%s" % longitude),
        }

        return info


class Port(models.Model):
    latitude = models.DecimalField(max_digits=7, decimal_places=5)
    longitude = models.DecimalField(max_digits=8, decimal_places=5)
    name = models.CharField(max_length=150)


class Guide(models.Model):
    port = models.ForeignKey(Port)
    title = models.CharField(max_length=150)
    date = models.DateTimeField()
    author = models.ForeignKey(Person)
    url = models.URLField(max_length=150)


class CruisingStation(models.Model):
    port = models.ForeignKey(Port)
    latitude = models.DecimalField(max_digits=7, decimal_places=5)
    longitude = models.DecimalField(max_digits=8, decimal_places=5)
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(max_length=100, blank=True)

    def get_info(self):
        info = {
            'portname': self.port.name,
            'name': self.name,
            'phone': self.phone,
            'email': self.email
        }

        return info
