from django.contrib.auth.models import User
from django.db import models
from gmapi import maps
from gmapi.forms.widgets import GoogleMap


class CoordinatesManager(models.Manager):
    def get_query_set(self):
        return self.filter(has_star=True)


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
    date = models.DateField()
    latitude = models.DecimalField(max_digits=8, decimal_places=5)
    longitude = models.DecimalField(max_digits=7, decimal_places=5)
    person = models.ForeignKey(Person)


class Coordinates(models.Model):
    latitude = models.DecimalField(max_digits=7, decimal_places=5)
    longitude = models.DecimalField(max_digits=8, decimal_places=5)
