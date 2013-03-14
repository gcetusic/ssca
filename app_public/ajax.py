import json

from dajaxice.decorators import dajaxice_register


@dajaxice_register(method='GET')
@dajaxice_register(method='POST', name='other_post')
def hello(request):
    print "-- hello --"
    return json.dumps({'message': 'hello'})


@dajaxice_register(method='GET')
@dajaxice_register(method='POST', name="more.complex.bye")
def bye(request):
    print "-- bye --"
    raise Exception("PUMMMM")
    return json.dumps({'message': 'bye'})


@dajaxice_register
def lol(request):
    print "-- lol --"
    return json.dumps({'message': 'lol'})


@dajaxice_register(method='GET')
def get_args(request, foo):
    print "-- owner --"
    return json.dumps({'message': 'hello get args %s' % foo})
