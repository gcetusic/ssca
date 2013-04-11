from django.contrib.auth import logout
from django.conf import settings
from django.shortcuts import render_to_response
from django.contrib.auth import login
from django.template import loader, RequestContext
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.core.urlresolvers import reverse
from django.core.xheaders import populate_xheaders
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_protect
from django.core.context_processors import csrf
from app_public.models import Person, Account, Page
from datetime import datetime
from decimal import *
import json
from app_public.forms import SSCAJoinForm
from django.core.mail import send_mail
from public_utils import *
from django.contrib.auth.models import User


def dashboard_main_page(request):
    return render_to_response('index.html')


def logout_page(request):
    """ Log users out and re-direct them to the main page. """
    logout(request)
    return HttpResponseRedirect(reverse('public-page'))


def member_page(request):
    """
    View for members page.
    """
    return render_to_response('member.html', {}, RequestContext(request))


def post_auth_process(request, backend, *args, **kwargs):
    """Post authentication process"""

    message = None

    try:  # Get the identity from the response returned by the OpenId provider.
        openid_identity = request.REQUEST['openid.identity']
        print "------> openid=", openid_identity

        # if we see that there openid_association flag is True in session
        # we will be associating person with openid
        if request.session.has_key('openid_association'):
            print "--> person id:", request.session['person_id']
            person_id = request.session['person_id']
            del request.session['person_id']
            del request.session['openid_association']
            print "--> session cleaned"
            person = Person.objects.get(id=person_id)
            person.identity = openid_identity
            person.save()

        try:  # Check whether an user exists with this Identity.
            person = Person.objects.get(identity=openid_identity)

            print "found person", person.__dict__

            # If exists, check whether the user has subscribed.
            account = Account.objects.get(user=person.user)

            # If subscribed, check whether the subscription is not expired.
            # If the subscription is not expired, login the user.
            current_date = datetime.now().date()
            if current_date >= account.subscription.start_date and \
               current_date <= account.subscription.end_date:
                user = person.user
                user.backend = 'social_auth.backends.google.GoogleBackend'
                login(request, person.user)
                print "---------------- Login Success redirect ----------------"
                return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)

            else:  # If the subscription seems to be expired, ask the user to renew it.
                print "---------------- Subscription Expired ----------------"
                message = {
                    'title': 'Subscription Expired',
                    'description': 'Your subscription seems to be expired. Please renew it.'
                }

        except Person.DoesNotExist:
            print "---------------- PersonDoesNotExist ----------------"
            context = {"error_type": "PersonDoesNotExist"}
            return render_to_response('public.html', RequestContext(request, context))

        except Account.DoesNotExist:
            print "-- Account DoesNotExist --"
            # If the user has no subscription yet, ask him to subscribe.
            message = {
                        'title': 'No Subscription found',
                        'description': 'You seem to be not chosen any subscription. Please subscribe.'
            }

    except KeyError:  # Handle the case of no identity found in the Openid provider response.
        # Message to the user as error in authentication.
        print "------> KeyError"
        message = {
            'title': 'Authentication Error',
            'description': 'There occurs error in authentication. Please try again.'
        }

    context = {"message": message}
    return render_to_response('error.html', RequestContext(request, context))


def join(request):
    """
    Function handles join popups. join form is shown if user has
    not already joined.

    :param request: django HttpRequest

    :return: django HttpResponse
    """
    #assuming new user
    user_exist = False
    form = SSCAJoinForm()
    c = {'form': form, 'basic_mail_cost': 55}
    return render_to_response('join.html', c)


def renew(request):
    """
    Function handles renew popups.

    :param request: django HttpRequest

    :return: django HttpResponse
    """
    return render_to_response('renew.html')


def public_page(request):
    #assuming new user
    user_exist = False
    form = SSCAJoinForm()
    c = {'form': form, 'basic_mail_cost': 55}
    c.update(csrf(request))
    return render_to_response('public.html', c, context_instance=RequestContext(request))

def registration_complete(request, token):
    response = HttpResponse()
    if not request.method == 'GET':
        response.write("ERROR:: Only HTTP GET is supported for registering.")
        return response

    print "registration complete:", token

    try:
        # TODO
        # (1) check token 
        person = Person.objects.get(signup_token = token)
        print person.__dict__

        signup_time = person.signup_date
        #current_time = datetime.now()
        from django.utils import timezone
        current_time = timezone.now()
        print ">>>> signup_time:", signup_time.date(), signup_time.time()
        print ">>>> current_time:", current_time.date(), current_time.time()
        #d1 = current_time.replace(tzinfo=None)
        #d2 = signup_time.replace(tzinfo=None)
        d1 = current_time
        d2 = signup_time
        print ">>>> diff=", (d1 - d2).days * 24
        #print ">>>> difference:", (current_time - signup_time).days * 24
        """
        if current_time - signup_time > 24:
            # token expired
            # removed person, user
            pass
        """

        # store the person id in session, so
        # that we can associate when we get callbacked by oauth provide
        request.session['person_id'] = person.id
        request.session['openid_association'] = True

        # (2) remove token from db

        # (3) check 24 hrs validity of token

        # (4) associate with OpenID

        c = {'registration_action': 'RegistrationComplete'}
        c.update(csrf(request))
        return render_to_response('public.html', c, context_instance=RequestContext(request))
    except Person.DoesNotExist:
        c = {'registration_action': 'RegistrationComplete_PersonDoesNotExist'}
        c.update(csrf(request))
        return render_to_response('public.html', c, context_instance=RequestContext(request))

@csrf_protect
def register_page(request):
    print "register_page()"
    response = HttpResponse()

    # print "checking request type"
    # we will only entertain POST request
    if not request.method == 'POST':
        response.write("ERROR:: Only HTTP POST is supported for registering.")
        return response

    # print "ensure email"
    if not request.POST.has_key("email"):
        response.write("ERROR:: Email not specified.")
        return response

    # print "ensure fname"
    if not request.POST.has_key("fname"):
        response.write("ERROR:: firstname not specified.")
        return response

    # print "ensure lname"
    if not request.POST.has_key("lname"):
        response.write("ERROR:: lastname not specified.")
        return response

    #todo fetch params from post request
    email = request.POST["email"]
    fname = request.POST["fname"]
    lname = request.POST["lname"]

    # print "name:", fname, lname

    # generate 64 byte hash
    token = get_rendon_alphanum64()

    # composing email
    subject = "SSCA Registration Activation"

    # FIXME - use actual url instead of localhost !!!
    link = "http://localhost:8000/registration/complete"
    email_format = """Hello %s, 
    Thank you very much for registering with SSCA.

    Kindly click on following link to activate your account:-
    %s/%s

    Sincerely,
    SSCA Team
    """
    name = "%s %s" % (fname, lname)
    email_body = email_format % (name, link, token)
    print email_body
    email_from = settings.EMAIL_HOST_USER

    # list of email receiver, we may add cc/bcc later
    email_to_lst = [] 

    email_to_lst.append(email)

    # send registration email
    send_mail(subject, email_body, email_from, email_to_lst, fail_silently=False)

    # create a new user and make him inactive
    print "creating user..."
    dummy_username = generate_random_str(30) # required

    new_user = User.objects.create_user(dummy_username, email)

    new_user.first_name = fname  # optional
    new_user.last_name = lname   # optional
    new_user.is_active = 0       # optional
    new_user.save()

    # add this user id as foreign key in person
    print "creating person..."
    new_person = Person()
    new_person.user = new_user
    new_person.signup_token = token
    new_person.save()

    response.write( "registering... %s" % request.POST["email"])
    return response

def dajax_test(request):
    """test view to evaluate dajax capabilities"""
    return render_to_response('dajax-test.html')


DEFAULT_TEMPLATE = 'flatpages/default.html'


@csrf_protect
def render_page(request, f):
    """
    Internal interface to the flat page view.
    """
    if f.template_name:
        t = loader.select_template((f.template_name, DEFAULT_TEMPLATE))
    else:
        t = loader.get_template(DEFAULT_TEMPLATE)

    # To avoid having to always use the "|safe" filter in flatpage templates,
    # mark the title and content as already safe (since they are raw HTML
    # content in the first place).
    f.title = mark_safe(f.title)
    f.content = mark_safe(f.content)

    picture = None
    if f.picture.exists():
        picture = mark_safe(f.picture.order_by('?')[0].render())

    c = RequestContext(request, {
        'page': f,
        'picture': picture
    })

    response = HttpResponse(t.render(c))
    populate_xheaders(request, response, Page, f.id)
    return response


def render_page_ajax(request, f):
    # To avoid having to always use the "|safe" filter in flatpage templates,
    # mark the title and content as already safe (since they are raw HTML
    # content in the first place).
    f.title = mark_safe(f.title)
    f.content = mark_safe(f.content)

    picture = None
    if f.picture.exists():
        picture = mark_safe(f.picture.order_by('?')[0].render())

    response = json.dumps({
        'title': f.title,
        'content': f.content,
        'picture': picture
    })

    return response


def sscapage(request, url):
    """
    Public interface to the page view.

    Models: `models.page`
    Templates: Uses the template defined by the ``template_name`` field,
        or `flatpages/default.html` if template_name is not defined.
    Context:
        flatpage
            `flatpages.flatpages` object
    """

    if not url.startswith('/'):
        url = '/' + url
    try:
        f = get_object_or_404(Page, url__exact=url, sites__id__exact=settings.SITE_ID)
    except Http404:
        if not url.endswith('/') and settings.APPEND_SLASH:
            url += '/'
            f = get_object_or_404(Page, url__exact=url, sites__id__exact=settings.SITE_ID)
            return HttpResponsePermanentRedirect('%s/' % request.path)
        else:
            raise

    # If registration is required for accessing this page, and the user isn't
    # logged in, redirect to the login page.
    if f.registration_required and not request.user.is_authenticated():
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(request.path)

    if request.is_ajax():
        return render_page_ajax(request, f)
    else:
        return render_page(request, f)
