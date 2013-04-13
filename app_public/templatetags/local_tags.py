from django import template
from app_public.models import MenuItem, MenuHeader, PageSequence, Page

register = template.Library()


@register.simple_tag
def show_ordered_flatpages():
    items = MenuItem.objects.filter(parent__isnull=True).order_by('-show_after')
    string = ""
    for item in items:
        string += get_ul_for_page(item)
    return string


def get_ul_for_page(item):
    items = MenuItem.objects.filter(parent=item).order_by('show_after')
    if len(items) < 1:
        if item.flatpage_parent.exists():
            url = item.flatpage_parent.order_by('?')[0].url
            li = """<li><a href="%s" data-page-type='page'>%s</a></li>""" % (url, item.title)
        else:
            li = """<li>%s</li>""" % (item.title)
        return li
    else:
        if item.flatpage_parent.exists():
            url = item.flatpage_parent.order_by('?')[0].url
            string = """<li><a href="%s">%s</a>""" % (url, item.title)
        else:
            string = """<li>%s""" % (item.title)
        string += "<ul>"
    for item in items:
        string += get_ul_for_page(item)  # recursion
    string += "</ul>"
    string += "</li>"
    return string


@register.filter
def get_full_name(user):
    """
    Returns the full name of the logged in user.
    """
    return "%s %s" % (user.first_name, user.last_name)


@register.filter
def get_ordered_pages(menu_header):
    """
    Returns an ordered list of Page objects based on the given menu_header parameter.
    The order will be based on sequence and in an ASC order.
    """
    return PageSequence.objects.filter(menu_header=menu_header).order_by('sequence')
