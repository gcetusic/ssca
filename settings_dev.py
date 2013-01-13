# Django settings for sscadev project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

STATIC_ROOT = 'static'

GOOGLE_MAPS_KEY = 'AIzaSyBAWy5kbUgK0t3Ly6VplTrem-dvpi-YuW8'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'ssca',                      # Or path to database file if using sqlite3.
        'USER': 'ssca',                      # Not used with sqlite3.
        'PASSWORD': 'ssca',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}
