'''
Holds all payment related functions.
'''
import braintree
from datetime import datetime
from app_payments.models import Transaction

def create_transaction(user, amount, card_number, cvv, expiration_month, 
                       expiration_year, purpose="Registration"):
    """
    Create a simple payment transaction on braintree. Recieves as input
    data about a credit card.    
    :param user: the user for which we are doing the transaction
    """
    result = braintree.Transaction.sale({
                "amount": amount,
                "credit_card": {
                    "number": card_number,
                    "cvv": cvv,
                    "expiration_month": expiration_month,
                    "expiration_year": expiration_year
                },
                "options": {
                    "submit_for_settlement": True
                }
            })
    transaction = Transaction(user = user, date = datetime.now(),
                              amount = amount, purpose = purpose)
    
    if result.is_success:
        transaction.transaction_id = result.transaction.id
        transaction.type = result.transaction.type
        transaction.save()
        return "Payment succesfull."
    else:
        # We have no transaction id or type if it failed
        transaction.error_message = result.message
        transaction.save()
        return result.message
    
    
def create_customer(first_name, last_name, postal_code, card_number, expiration_month, 
                    expiration_year, cvv):
    """
    Braintree offers possibility to create a customer. After this you get a customer
    id which can later be used to get informations like credit card info if we want.
    :params first_name, last_name:  We might as well store these on a Person entity 
                                    and pass that as input.
    NOTE: this does not create a transaction, just a customer.
    """
    result = braintree.Customer.create({
                "first_name": first_name,
                "last_name": last_name,
                "credit_card": {
                    "number": card_number,
                    "expiration_month": expiration_month,
                    "expiration_year": expiration_year,
                    "cvv": cvv
                }
            })
    if result.is_success:
        # result.customer.id can be stored on a Person entity so we can later
        # on return the same customer and get various information (eg. credit-cards)
        pass
    else:
        return result.message
    

def create_recurring_billing(customer_id):
    """
    Create a subscription type payment plan using braintree. Note: you
    have to first create the plan on braintree with a given ID that you will later
    on be using here. 
    NOTE: For now I've created a 'test_plan_1', I'll just let it here since I'm not
    sure we want to use this alternative or handle on our own the subscriptors payments.
    """
    TEST_RECURRING_PLAN_ID = "test_plan_1"
    # Get the braintree customer using the id we get from the 
    # create_customer method
    customer = braintree.Customer.find(customer_id)
    # Get the first credit card registered to this user (for now).
    payment_method_token = customer.credit_cards[0].token
    result = braintree.Subscription.create({
            "payment_method_token": payment_method_token,
            "plan_id": TEST_RECURRING_PLAN_ID
        })
    if result.is_success:
        """
        Again we can store id from here in Subscription model maybe if want to later get it with
        braintree.Subscription.find(id) and get various information from there.
        """
        pass
    else:
        return result.message

    
