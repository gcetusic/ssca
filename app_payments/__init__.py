import braintree
from django.conf import settings

# Configure braintree to use the keys for our account.
braintree.Configuration.configure(settings.BTREE_ENVIRONMENT,
                                  settings.BTREE_MERCHANT_ID,
                                  settings.BTREE_PUBLIC_KEY,
                                  settings.BTREE_PRIVATE_KEY)