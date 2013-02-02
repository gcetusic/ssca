from .models import Location, Person
from django.contrib.auth.models import User
from django.utils import timezone
import decimal
import random


def gen_random_position(latrange, lonrange):
    latitude = decimal.Decimal('%d.%d' % (random.randint(latrange[0], latrange[1]), random.randint(0, 99999)))
    longitude = decimal.Decimal('%d.%d' % (random.randint(lonrange[0], lonrange[1]), random.randint(0, 99999)))

    return (latitude, longitude)


def write_data(latrange=(-89, 89), lonrange=(-179, 179), limit=10000):
    if Person.objects.all().exists():
        person = Person.objects.order_by('?')[0]
    else:
        if User.objects.all().exists():
            user = User.objects.order_by('?')[0]
        else:
            user = User(username=str(random.randint(0, 1000000)))
            user.save()
        person = Person(user=user, identity=str(random.randint(0, 1000000)))
        person.save()

    locations = []
    for i in range(limit):
        position = gen_random_position(latrange, lonrange)
        locations.append(Location( \
                                date=timezone.now(), \
                                latitude=position[0], longitude=position[1], \
                                person=person))
    Location.objects.bulk_create(locations)


def delete_data():
    Location.objects.all().delete()
