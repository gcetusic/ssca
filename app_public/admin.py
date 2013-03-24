from django.contrib import admin
from app_public.models import Person, Account, Subscription
from django.contrib.flatpages.admin import FlatpageForm, FlatPageAdmin
from django.contrib.flatpages.models import FlatPage

from app_public.models import Page


class ExtendedFlatPageForm(FlatpageForm):
    class Meta:
        model = Page


class ExtendedFlatPageAdmin(FlatPageAdmin):
    form = ExtendedFlatPageForm
    fieldsets = ((None, {'fields': ('url', 'title', 'content', 'picture', 'show_after', 'child_of', 'sites')}),)

admin.site.unregister(FlatPage)
admin.site.register(Page, ExtendedFlatPageAdmin)
admin.site.register(Person)
admin.site.register(Account)
admin.site.register(Subscription)
