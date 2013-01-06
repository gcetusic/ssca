from django.contrib.auth.models import User
from django.db import models

class Subscription(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
    amount_paid = models.DecimalField(max_digits=3, decimal_places=2)
    date_paid = models.DateField()

class Account(models.Model):
    user = models.ForeignKey(User)
    subscription = models.ForeignKey(Subscription)

class Person(models.Model):
    user = models.ForeignKey(User)
    # openid identity string, used to find which User has logged in
    identity = models.TextField()
