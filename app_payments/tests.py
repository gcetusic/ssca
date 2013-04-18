"""
Full list of valid credit card numbers the sandbox accepts.

https://www.braintreepayments.com/docs/ruby/reference/sandbox

NOTE: running tests too quickly one after another might cause braintree
to refuse some transactions.
"""
import os
import unittest
import datetime
import braintree
from app_payments.payment_service import create_transaction, create_subscription, validate_card_details
from app_payments.export_payment_service import quickbooks_export_transactions
from app_payments.braintree_finders_API import get_transactions_before, get_transactions_in_date_inverval, \
get_transactions_with_amount_range
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
        
    def test_card_details_valid(self):
        validate_card_details('Raymond', 'Hettinger', '5555555555554444', '223', 
                                       '05', '14')
    
    def test_card_details_invalid_card(self):
        """
        Pass some data that should be rejected due to card number.
        """
        self.assertRaises(InvalidCardDetails, validate_card_details, 'Raymond', 'Hettinger', 
                          '5555555111554444', '223', '05', '14')
        
    def test_get_transactions_before_old_date(self):
        """
        Test that we don't get any transactions if we try before some
        old date.
        """
        old_date = datetime.datetime(1901, 1, 13)
        result = get_transactions_before(old_date)
        self.assertEqual(len(list(result)), 0)


    def test_get_transactions_before_now(self):
        """
        We can't know exactly how many transactions we have since each
        test run generates new ones. Just test that it returs something
        since we should have transactions older than todat.
        """
        result = get_transactions_before(datetime.datetime.now())
        self.assertTrue(len(list(result)) > 0)
        
    
    def test_quickbook_export(self):
        """
        Just get all transactions and export them to a csv file. No exceptions
        or erros are expected. File should be present in app_payments folder, named
        all_transactions.csv
        """
        result_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                   'all_transactions.csv')
        trans_list = get_transactions_before()
        quickbooks_export_transactions(trans_list, result_file)
        
        
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
        transaction = create_transaction(100, '5555555555554444', '223', 5, 2016, user=self.user)
        self.assertEqual(transaction.amount, 100)
        self.assertEqual(transaction.user.id, self.user.id)
        braintree_trans = braintree.Transaction.find(transaction.transaction_id)
        user = Person.objects.filter(id=self.user.id)[0]
        self.assertEqual(user.customer_id, braintree_trans.customer_details.id)
        
        
    def test_create_subscription(self):
        """
        Use case to create a subscription.
        """
        subscription = create_subscription(self.user, 100, '5555555555554444', 5, 2016, '223')
        braintree_subs = braintree.Subscription.find(subscription.braintree_id)
        self.assertEqual(braintree_subs.id, subscription.braintree_id)
        braintree.Subscription.cancel(braintree_subs.id)
        

    def test_create_transaction_invalid_card(self):
        """
        Pass a credit card that is not supported to a transaction.
        """
        self.user.save()
        self.assertRaises(InvalidCardDetails, create_transaction, 100, 
                          '5555511555554444', '223', 5, 2016, user=self.user)
        
        
    def test_create_subscription_invalid_id(self):
        """
        Use case to create a subscription.
        """
        self.assertRaises(InvalidSubscriptionId, create_subscription, self.user, 100, 
                          '5555555555554444', 5, 2016, '223', 
                          braintree_plan_id="this_should_not_exist")
        
        