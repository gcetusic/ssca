"""
Full list of valid credit card numbers the sandbox accepts.

https://www.braintreepayments.com/docs/ruby/reference/sandbox

NOTE: running tests too quickly one after another might cause braintree
to refuse some transactions.
"""
import unittest
import braintree
from app_payments.payment_service import create_transaction, create_subscription
from app_public.models import Person
from django.contrib.auth.models import User

class TransactionTestCase(unittest.TestCase):
    
    def test_create_simple_transaction_valid(self):
        """
        Create a transaction with no user passed. 
        """
        transaction = create_transaction(100, '4005519200000004', '112', 3, 2014)
        self.assertEqual(transaction.amount, 100)
        self.assertTrue(transaction.user is None)
        braintree_trans = braintree.Transaction.find(transaction.transaction_id)
        self.assertEqual(braintree_trans.amount, 100)
        self.assertEqual(braintree_trans.credit_card['bin'], '400551')
        self.assertEqual(braintree_trans.credit_card['expiration_month'], '03')
        self.assertEqual(braintree_trans.credit_card['expiration_year'], '2014')
        self.assertEqual(braintree_trans.credit_card['card_type'], 'Visa')
        
        
    def test_create_transaction_for_user(self):
        """
        We have a user but we don't have a customer id yet for him.
        """
        base_user = User(first_name="Guido", last_name="Van Rossum",)
        base_user.save()
        user = Person(user=base_user)
        user.save()
        transaction = create_transaction(100, '5555555555554444', '223', 5, 2016, user=user)
        self.assertEqual(transaction.amount, 100)
        self.assertEqual(transaction.user.id, user.id)
        braintree_trans = braintree.Transaction.find(transaction.transaction_id)
        user = Person.objects.filter(id=user.id)[0]
        self.assertEqual(user.customer_id, braintree_trans.customer_details.id)
        user.delete()
        base_user.delete()
        
        
    def test_create_subscription(self):
        """
        Use case to create a subscription.
        """
        base_user = User(first_name="Guido", last_name="Van Rossum",)
        base_user.save()
        user = Person(user=base_user)
        user.save()
        subscription = create_subscription(user, 100, '5555555555554444', 5, 2016, '223')
        braintree_subs = braintree.Subscription.find(subscription.braintree_id)
        self.assertEqual(braintree_subs.id, subscription.braintree_id)
        braintree.Subscription.cancel(braintree_subs.id)
        user.delete()
        base_user.delete()
        
        
        