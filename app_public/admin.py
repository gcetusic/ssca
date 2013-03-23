from django.contrib import admin
from app_public.models import Person, Account, Subscription
from django.contrib.flatpages.admin import FlatpageForm, FlatPageAdmin
from django.contrib.flatpages.models import FlatPage as BaseFlatPage

from app_public.models import FlatPage


class ExtendedFlatPageForm(FlatpageForm):
    class Meta:
        model = FlatPage


class ExtendedFlatPageAdmin(FlatPageAdmin):
    form = ExtendedFlatPageForm
    fieldsets = (
        (None, {'fields': ('url', 'title', 'content', 'sites', 'order')}),
    )

admin.site.unregister(BaseFlatPage)
admin.site.register(FlatPage, ExtendedFlatPageAdmin)
admin.site.register(Person)
admin.site.register(Account)
admin.site.register(Subscription)
