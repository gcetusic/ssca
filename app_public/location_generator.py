from .models import Location
from datetime import datetime
import decimal
import random


def gen_random_position():
    latitude = decimal.Decimal('%d.%d' % (random.randint(-89, 89), random.randint(0, 99999)))
    longitude = decimal.Decimal('%d.%d' % (random.randint(-179, 179), random.randint(0, 99999)))

    return (latitude, longitude)


def write_data(limit=10000):
    for i in range(limit):
        position = gen_random_position()
        location = Location(date=datetime.now(), latitude=position[0], longitude=position[1])
        location.save()
