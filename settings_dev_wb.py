# Django settings for sscadev project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

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

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'test.weavebytes@gmail.com'
EMAIL_HOST_PASSWORD = 'test@1234'
EMAIL_PORT = 587

# ------------ Braintree payments related keys start here ------------

import braintree
BTREE_ENVIRONMENT = braintree.Environment.Sandbox
BTREE_MERCHANT_ID = "qp96bcphs85fyjyq"
BTREE_PUBLIC_KEY = "ccsmkms74ymxhbxg"
BTREE_PRIVATE_KEY = "5227ce9f17856c06e877871eefb8e92a"

# ------------ Braintree payments keys end here           ------------