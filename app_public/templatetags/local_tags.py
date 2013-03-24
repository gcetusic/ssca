from django import template
from app_public.models import MenuItem

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
            li = """<li><a href="%s">%s</a></li>""" % (url, item.title)
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


# def get_unique_paths(items, sizes):
#     unique_paths = []

#     for i in range(len(parents)+1):
#         print i
#         for child in children:
#             parent = parents[i]

#     return unique_paths


# def common_prefix(strings):
#     """ Find the longest string that is a prefix of all the strings.
#     """
#     if not strings:
#         return ''
#     prefix = strings[0]
#     for s in strings:
#         if len(s) < len(prefix):
#             prefix = prefix[:len(s)]
#         if not prefix:
#             return ''
#         for i in range(len(prefix)):
#             if prefix[i] != s[i]:
#                 prefix = prefix[:i]
#                 break
#     return prefix

# def gpt():
#     menu_paths = []
#     for item in MenuItem.objects.all():
#         menu_paths.append(item.__repr__())
#     menu_paths = set(menu_paths)

#     items_by_size = {}
#     separator = MenuItem().get_separator()

#     sizes = []
#     for path in menu_paths:
#         size = len(path.rsplit(separator))
#         sizes.append(size)
#         if size in items_by_size:
#             items_by_size[size].append(path)
#         else:
#             items_by_size[size] = [path]

#     sizes = sorted(set(sizes))

#     unique_paths = get_unique_paths(items_by_size, sizes)
#     print unique_paths
