from django import template
from app_public.models import Page

register = template.Library()


@register.simple_tag
def show_ordered_flatpages():
    flat_pages = Page.objects.filter(child_of__isnull=True).order_by('-show_after')
    string = ""
    for page in flat_pages:
        string += get_ul_for_page(page)
    return string


def get_ul_for_page(page):
    flat_pages = Page.objects.filter(child_of=page).order_by('show_after')
    if len(flat_pages) < 1:
        return """<li><a href="%s">%s</a></li>""" % (page.url, page.title)
    else:
        string = """<li><a href="%s">%s</a>""" % (page.url, page.title)
        string += "<ul>\n"
    for page in flat_pages:
        string += get_ul_for_page(page)  # recursion
    string += "</ul>\n"
    string += "</li>\n"
    return string
