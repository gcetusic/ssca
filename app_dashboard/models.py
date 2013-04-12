from django.db import models
from django.utils import timezone
from django.utils.timezone import get_current_timezone
from datetime import timedelta
from app_public.models import Person
import math
import re


class LocationManager(models.Manager):
    def current_location(self, change, user_ids=None):
        '''
            The method takes the number of minutes as the 'change' argument.
            A value of 0 means the most recent record is fetched.

            If given a list of ids, it fetches only Locations with those user ids
            The returned value is a list with location ids
        '''
        if not change == 0:
            location_ids = super(LocationManager, self).get_query_set().filter(
                date__gte=(timezone.now() - timedelta(minutes=change))).values_list('id', flat=True)
        else:
            if user_ids:
                person_ids = Person.objects.filter(user_id__in=user_ids).values_list('id', flat=True)
            else:
                person_ids = Person.objects.all().values_list('id', flat=True)

            location_ids = []
            locations_by_person = super(LocationManager, self).get_query_set().filter(person_id__in=person_ids)

            for person_id in person_ids:
                location_by_person = locations_by_person.filter(person_id=person_id)
                if location_by_person.exists():
                    location_ids.append(location_by_person.latest('date').id)

        return location_ids


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

    @staticmethod
    def format_coordinates(coordinate):
        minutes, degrees = math.modf(round(coordinate, 4))
        degrees = "%d" % degrees
        minutes = "%.2f" % round(minutes * 60, 2)
        return degrees + " " + minutes

    def get_info(self):
        usertime = self.date.astimezone(get_current_timezone())
        latitude, longitude = Location.to_readable_format(self.latitude,self.longitude)
        info = {
            'name': self.person.user.username,
            'date': usertime.strftime("%Y-%m-%d %H:%m"),
            'position': ("%s" % latitude, "%s" % longitude),
        }

        return info

    @staticmethod
    def to_readable_format(latitude, longitude):
        if latitude >= 0:
            readable_latitude = 'N'
        else:
            readable_latitude = 'S'

        if longitude >= 0:
            readable_longitude = 'E'
        else:
            readable_longitude = 'W'

        readable_latitude += Location.format_coordinates(latitude)
        readable_longitude += Location.format_coordinates(longitude)

        return readable_latitude, readable_longitude

    @staticmethod
    def to_decimal_format(location):
        pattern = re.compile('^[N|S|n|s](\d{2}) (\d{2}.\d{2}), [W|E|w|e](\d{3}) (\d{2}.\d{2})$')
        m = pattern.match(location)
        latitude_deg = int(m.groups(0)[0])
        latitude_min = float(m.groups(0)[1])
        longitude_deg = int(m.groups(0)[2])
        longitude_min = float(m.groups(0)[3])

        dec_latitude = latitude_deg + latitude_min / 60
        dec_longitude = longitude_deg + longitude_min / 60
        return dec_latitude, dec_longitude



class Port(models.Model):
    latitude = models.DecimalField(max_digits=7, decimal_places=5)
    longitude = models.DecimalField(max_digits=8, decimal_places=5)
    name = models.CharField(max_length=150)

    def __unicode__(self):
        return u'%s' % (self.name)


class Guide(models.Model):
    port = models.ForeignKey(Port)
    title = models.CharField(max_length=150)
    date = models.DateTimeField()
    author = models.ForeignKey(Person)
    url = models.URLField(max_length=150)

    def get_info(self):
        usertime = self.date.astimezone(get_current_timezone())
        info = {
            'portname': self.port.name,
            'title': self.title,
            'date': usertime.strftime("%Y-%m-%d %H:%m"),
            'author': self.author.user.username,
        }

        return info

    def __unicode__(self):
        return u'%s' % (self.title)


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

    def __unicode__(self):
        return u'%s' % (self.name)
