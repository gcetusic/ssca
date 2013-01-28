from .models import Location
from datetime import datetime
from django.db.models.query import QuerySet
import decimal
import random


def gen_random_position(latrange, lonrange):
    latitude = decimal.Decimal('%d.%d' % (random.randint(latrange[0], latrange[1]), random.randint(0, 99999)))
    longitude = decimal.Decimal('%d.%d' % (random.randint(lonrange[0], lonrange[1]), random.randint(0, 99999)))

    return (latitude, longitude)


def write_data(latrange=(-89, 89), lonrange=(-179, 179), limit=10000):
    locations = []
    for i in range(limit):
        position = gen_random_position(latrange, lonrange)
        locations.append(Location(date=datetime.now(), latitude=position[0], longitude=position[1]))
    Location.objects.bulk_create(locations)
