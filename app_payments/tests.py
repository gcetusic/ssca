"""
Full list of valid credit card numbers the sandbox accepts.

https://www.braintreepayments.com/docs/ruby/reference/sandbox

NOTE: running tests too quickly one after another might cause braintree
to refuse some transactions.
"""
import unittest
import braintree
from app_payments.payment_service import create_transaction, create_subscription
from app_payments.export_payment_service import _get_all_transactions
from app_payments.exceptions import *
from app_public.models import Person
from django.contrib.auth.models import User

class TransactionTestCase(unittest.TestCase):
    
    def setUp(self):
        self.b_user = User(first_name="Guido", last_name="Van Rossum",)
        self.b_user.save()
        self.user = Person(user=self.b_user)
        self.user.save()
        
        
    def tearDown(self):
        self.b_user.delete()
        self.user.delete()
        
    
    def test_all_trans(self):
        trans_res = _get_all_transactions()
        import pdb
        pdb.set_trace()
    
    
#    def test_create_simple_transaction_valid(self):
#        """
#        Create a transaction with no user passed. 
#        """
#        transaction = create_transaction(100, '4005519200000004', '112', 3, 2014)
#        self.assertEqual(transaction.amount, 100)
#        self.assertTrue(transaction.user is None)
#        braintree_trans = braintree.Transaction.find(transaction.transaction_id)
#        self.assertEqual(braintree_trans.amount, 100)
#        self.assertEqual(braintree_trans.credit_card['bin'], '400551')
#        self.assertEqual(braintree_trans.credit_card['expiration_month'], '03')
#        self.assertEqual(braintree_trans.credit_card['expiration_year'], '2014')
#        self.assertEqual(braintree_trans.credit_card['card_type'], 'Visa')
#        
#        
#    def test_create_transaction_for_user(self):
#        """
#        We have a user but we don't have a customer id yet for him.
#        """
#        transaction = create_transaction(100, '5555555555554444', '223', 5, 2016, user=self.user)
#        self.assertEqual(transaction.amount, 100)
#        self.assertEqual(transaction.user.id, self.user.id)
#        braintree_trans = braintree.Transaction.find(transaction.transaction_id)
#        user = Person.objects.filter(id=self.user.id)[0]
#        self.assertEqual(user.customer_id, braintree_trans.customer_details.id)
#        
#        
#    def test_create_subscription(self):
#        """
#        Use case to create a subscription.
#        """
#        subscription = create_subscription(self.user, 100, '5555555555554444', 5, 2016, '223')
#        braintree_subs = braintree.Subscription.find(subscription.braintree_id)
#        self.assertEqual(braintree_subs.id, subscription.braintree_id)
#        braintree.Subscription.cancel(braintree_subs.id)
#
#    
#    def test_create_transaction_invalid_name(self):
#        """
#        Pass a name that is too long for a customer.
#        """
#        self.b_user.first_name = ''.join(['a' for _ in xrange(266)]) # max 255 chars for name
#        self.b_user.save()
#        self.assertRaises(InvalidCustomerData, create_transaction, 100, 
#                          '5555555555554444', '223', 5, 2016, user=self.user)
#
#
#    def test_create_transaction_invalid_card(self):
#        """
#        Pass a credit card that is not supported to a transaction.
#        """
#        self.user.save()
#        self.assertRaises(InvalidTransactionParameters, create_transaction, 100, 
#                          '5555511555554444', '223', 5, 2016, user=self.user)
#        
#        
#    def test_create_subscription_invalid_id(self):
#        """
#        Use case to create a subscription.
#        """
#        self.assertRaises(InvalidSubscriptionId, create_subscription, self.user, 100, 
#                          '5555555555554444', 5, 2016, '223', 
#                          braintree_plan_id="this_should_not_exist")
        
        