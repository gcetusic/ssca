from django.contrib.auth.models import User
from django.db import models
import math


class Subscription(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
    amount_paid = models.DecimalField(max_digits=5, decimal_places=2)
    date_paid = models.DateField()


class Account(models.Model):
    user = models.ForeignKey(User)
    subscription = models.ForeignKey(Subscription)


class Person(models.Model):
    user = models.ForeignKey(User)
    # openid identity string, used to find which User has logged in
    identity = models.TextField()


class Location(models.Model):
    date = models.DateTimeField()
    latitude = models.DecimalField(max_digits=7, decimal_places=5)
    longitude = models.DecimalField(max_digits=8, decimal_places=5)
    person = models.ForeignKey(Person, blank=True, null=True)

    def decimal_to_float(self, location, *args):
        for arg in args:
            location[arg] = float(location[arg])
        return location

    def format_coordinates(self, coordinate):
        minutes, degrees = math.modf(round(coordinate, 4))
        degrees = "%d" % degrees
        minutes = "%.2f" % round(minutes * 60, 2)
        return degrees + " " + minutes


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
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(max_length=100, blank=True)
