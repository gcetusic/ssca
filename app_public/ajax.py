import simplejson

from dajaxice.decorators import dajaxice_register


@dajaxice_register(method='GET')
@dajaxice_register(method='POST', name='other_post')
def hello(request):
    print "-- hello --"
    return simplejson.dumps({'message': 'hello'})


@dajaxice_register(method='GET')
@dajaxice_register(method='POST', name="more.complex.bye")
def bye(request):
    print "-- bye --"
    raise Exception("PUMMMM")
    return simplejson.dumps({'message': 'bye'})


@dajaxice_register
def lol(request):
    print "-- lol --"
    return simplejson.dumps({'message': 'lol'})


@dajaxice_register(method='GET')
def get_args(request, foo):
    print "-- owner --"
    return simplejson.dumps({'message': 'hello get args %s' % foo})
