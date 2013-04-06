from django.shortcuts import render_to_response
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse

from app_backoffice.jqgrid import JqGrid

class UserGrid(JqGrid):
    fields = ("id", "username", "first_name", "last_name", "email", "date_joined", "last_login")
    model = User
    pager_id = '#pager_doc'
    url = reverse_lazy('grid_handler')
    caption = 'List of Members' # optional
    colmodel_overrides = {
        'id': { 'editable': False, 'width':50, 'sortable': True },
        'username': { 'editable': False, 'width':50, 'sortable': True },
        'first_name': { 'editable': False, 'width':150, 'sortable': True  },
        'last_name': { 'editable': False, 'width':150, 'sortable': True  },
        'email': { 'editable': False, 'width':150, 'sortable': True  },
        'date_joined': { 'editable': False, 'width':100, 'sortable': True  },
        'last_login': { 'editable': False, 'width':100, 'sortable': True  },
    }
    
@staff_member_required
def grid_handler(request):
    # handles pagination, sorting and searching
    grid = UserGrid()
    return HttpResponse(grid.get_json(request), mimetype="application/json")

@staff_member_required
def grid_config(request):
    # build a config suitable to pass to jqgrid constructor   
    grid = UserGrid()
    return HttpResponse(grid.get_config(), mimetype="application/json")
   
@staff_member_required   
def backoffice_main_page(request):
    """ The page onlt for Admin use """
    variables = RequestContext(request, {})
    return render_to_response('backoffice/index.html', variables)



