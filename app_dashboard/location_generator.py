from app_dashboard.models import Location, Port, Guide, CruisingStation
from app_public.models import Person
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

    ports = []
    for i in range(limit):
        position = gen_random_position(latrange, lonrange)
        ports.append(Port( \
                                latitude=position[0], longitude=position[1], \
                                name=str(random.randint(0, 1000000))))
    Port.objects.bulk_create(ports)

    if Port.objects.all().exists():
        ports = Port.objects.order_by('?')

    guides = []
    stations = []
    for port in ports:
        guides.append(Guide( \
                                date=timezone.now(), \
                                title=str(random.randint(0, 1000000)), \
                                url="http://localhost:8000",
                                author=person,
                                port=port))
        position = gen_random_position(latrange, lonrange)
        stations.append(CruisingStation( \
                                latitude=position[0], longitude=position[1], \
                                name=str(random.randint(0, 1000000)), \
                                phone=str(random.randint(0, 1000000)), \
                                email="no@mail.com",
                                port=port))

    Guide.objects.bulk_create(guides)
    CruisingStation.objects.bulk_create(stations)


def delete_data():
    Location.objects.all().delete()
    Port.objects.all().delete()
    Guide.objects.all().delete()
    CruisingStation.objects.all().delete()
