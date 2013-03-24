from django.contrib import admin
from app_public.models import Person, Account, Subscription
from django.contrib.flatpages.admin import FlatpageForm, FlatPageAdmin
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site

from app_public.models import Page


class ExtendedFlatPageForm(FlatpageForm):
    class Meta:
        model = Page


class ExtendedFlatPageAdmin(FlatPageAdmin):
    form = ExtendedFlatPageForm
    fieldsets = ((None, {'fields': ('url', 'title', 'content', 'picture', 'show_after', 'child_of', 'sites')}),)

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == "sites":
            kwargs["initial"] = [Site.objects.get_current()]
        return super(FlatPageAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.unregister(FlatPage)
admin.site.register(Page, ExtendedFlatPageAdmin)
admin.site.register(Person)
admin.site.register(Account)
admin.site.register(Subscription)
