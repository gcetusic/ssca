from django.contrib import admin
from app_public.models import Person, Account, Subscription

# Register in the admin interface.
admin.site.register(Person)
admin.site.register(Account)
admin.site.register(Subscription)
