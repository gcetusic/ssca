from django.db import models

from app_public.models import Person
'''
Full list of attributes avaliable on a braintree's SuccessfulResult.transaction
object. Don't think we need to keep track of anything else. 

'add_ons', 'amount', 'avs_error_response_code', 'avs_postal_code_response_code', 
'avs_street_address_response_code', 'billing', 'billing_details', 'channel', 
'clone_signature', 'clone_transaction', 'confirm_transparent_redirect', 
'create', 'create_signature', 'created_at', 'credit', 'credit_card', 'credit_card_details', 
'currency_iso_code', 'custom_fields', 'customer', 'customer_details', 'cvv_response_code', 
'descriptor', 'discounts', 'find', 'gateway', 'gateway_rejection_reason', 'id', 
'merchant_account_id', 'order_id', 'plan_id', 'processor_authorization_code', 
'processor_response_code', 'processor_response_text', 'purchase_order_number', 
'recurring', 'refund', 'refund_id', 'refund_ids', 'refunded_transaction_id', 'sale', 
'search', 'settlement_batch_id', 'shipping', 'shipping_details', 'status', 
'status_history', 'submit_for_settlement', 'subscription', 'subscription_details', 
'subscription_id', 'tax_amount', 'tax_exempt', 'tr_data_for_credit', 'tr_data_for_sale', 
'transparent_redirect_create_url', 'type', 'updated_at', 'vault_billing_address', 
'vault_credit_card', 'vault_customer', 'verify_keys', 'void'
'''
class Transaction(models.Model):
    user = models.ForeignKey(Person, null=True, blank=True)
    date = models.DateField()
    amount = models.FloatField()
    purpose = models.CharField(max_length=300)
    transaction_id = models.CharField(max_length=30)
    error_message = models.CharField(max_length=300)
    type = models.CharField(max_length=30)