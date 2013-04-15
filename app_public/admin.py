from django.contrib import admin
from app_public.models import Person, Account, Subscription, Image, MenuItem, MenuHeader, \
    PageSequence
from django.contrib.flatpages.admin import FlatpageForm, FlatPageAdmin
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from app_public.models import Page


class ExtendedFlatPageForm(FlatpageForm):
    class Meta:
        model = Page


class ExtendedFlatPageAdmin(FlatPageAdmin):
    form = ExtendedFlatPageForm
    fieldsets = (
        (None, {'fields': ('url', 'title', 'page_type', 'require_authentication', 'content', 
                'picture', 'child_of', 'sites')}),
        (('Advanced options'), {'classes': ('collapse',), 'fields': ('enable_comments', 'registration_required', 'template_name')}),
    )

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == "sites":
            kwargs["initial"] = [Site.objects.get_current()]
        return super(FlatPageAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class PageSequenceAdmin(admin.ModelAdmin):
    """
    Admin for PageSequence model
    """
    model = PageSequence
    list_display = ['menu_header', 'page', 'sequence']

admin.site.unregister(FlatPage)
admin.site.register(Page, ExtendedFlatPageAdmin)
admin.site.register(MenuItem)
admin.site.register(MenuHeader)
admin.site.register(Image)
admin.site.register(Person)
admin.site.register(Account)
admin.site.register(Subscription)
admin.site.register(PageSequence, PageSequenceAdmin)
