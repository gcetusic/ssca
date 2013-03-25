from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required


@login_required
def dashboard_main_page(request):
    """ If users are authenticated, direct them to the main page. Otherwise,
        take them to the login page. """
    return render_to_response('dashboard/index.html')


def dashboard_test_mockup(request):
    """ test view for dashboard mockup """
    return render_to_response('dashboard/index.html')
