from django.contrib.auth.models import User
from django.db import models

class Subscription(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
    amount_paid = models.DecimalField(max_digits=5, decimal_places=2)
    date_paid = models.DateField()


class Account(models.Model):
    # TODO i don't think this should have a user...should it?
    user = models.ForeignKey(User)
    subscription = models.ForeignKey(Subscription)
    def __unicode__(self):
        return u'%s' % (self.user.username)

class Person(models.Model):
    user = models.ForeignKey(User)
    # openid identity string, used to find which User has logged in
    identity = models.TextField()
    friend =  models.ManyToManyField('self', through='Relationship', symmetrical=False)

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

class Relationship(models.Model):
    from_person = models.ForeignKey(Person, related_name='from_people')
    to_person = models.ForeignKey(Person, related_name='to_people')

# this is just so that the app-wide sample data works (we don't have data for it yet)
class Dev(models.Model):
    test = models.TextField()
