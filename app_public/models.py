from django.contrib.auth.models import User
from django.db import models

from django.contrib.flatpages.models import FlatPage as BaseFlatPage


class FlatPage(BaseFlatPage):
    order = models.PositiveIntegerField(unique=True)
    picture = models.ImageField(upload_to='pages')


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

    # FIXME - need to determine how to store this info in db
    # encrypt or hash ?
    """
    card_number = models.CharField(max_length=32, required = True)
    card_expiry_date = models.DateField(required = True)
    card_csv = models.CharField(max_length=3, required = True)
    yearly_total = models.IntegerField()
    yearly_reniew = models.BooleanField() 
    total = models.IntegerField()
    """


class Location(models.Model):
    date = models.DateTimeField()
    latitude = models.DecimalField(max_digits=7, decimal_places=5)
    longitude = models.DecimalField(max_digits=8, decimal_places=5)
    person = models.ForeignKey(Person, blank=True, null=True)
