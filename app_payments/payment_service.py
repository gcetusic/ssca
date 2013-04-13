'''
Holds all payment related functions.
'''
import braintree
from datetime import datetime
from app_public.models import Subscription
from app_payments.models import Transaction
from app_payments.error_handler import _handle_subscription_failure,\
    _handle_customer_failure, _handle_transaction_failure


def create_transaction(amount, card_number, cvv, expiration_month, 
                       expiration_year, user=None, purpose="Registration"):
    """
    Create a simple payment transaction on braintree. Recieves as input
    data about a credit card.    
    :param user: the user for which we are doing the transaction.
    
    If :param user: is None then we fallback to creating a simple transaction with
    the miminum data accepted. Otherwise if user has a valid customer_id then we
    use that for the transaction, if not we generate a new customer and save the
    customer_id.
    """
    if user is None:
        # No user, create simple transaction
        result = _create_simple_transaction(amount, card_number, cvv, expiration_month, 
                                          expiration_year)
    elif user.get_customer_id():
        # We have a user and customer, create transaction using their id.
        customer_id = user.get_customer_id()
        result = _create_transaction_for_customer(customer_id, amount, card_number, cvv, 
                                                expiration_month, expiration_year)
    else:
        # We have a user that is not yet customer, create customer and transaction.
        first_name = user.user.first_name
        last_name = user.user.last_name
        result = _create_customer_and_transaction(first_name, last_name, amount, card_number, cvv, 
                                                expiration_month, expiration_year)
        user.customer_id = result.transaction.customer_details.id
        user.save()
    transaction = Transaction(user = user, date = datetime.now(),
                              amount = amount, purpose = purpose)
    if result.is_success:
        transaction.transaction_id = result.transaction.id
        transaction.type = result.transaction.type
        transaction.save()
        return transaction
    else:
        # We have no transaction id or type if it failed
        transaction.error_message = result.message
        transaction.save()
        _handle_transaction_failure(result)
    
    
def create_subscription(user, amount, card_number, expiration_month, 
                        expiration_year, cvv, braintree_plan_id="test_plan_1"):
    """
    Create a subscription type payment plan using braintree. Note: you
    have to first create the plan on braintree with a given ID that you will later
    on be using here. 
    NOTE: For now I've created a 'test_plan_1', I'll just let it here since I'm not
    sure we want to use this alternative or handle on our own the subscriptors payments.
    """
    if user.get_customer_id() is None:
        first_name = user.user.first_name
        last_name = user.user.last_name
        customer_id = _create_customer(first_name, last_name, card_number, expiration_month, 
                                       expiration_year, cvv)
        user.customer_id = customer_id
        user.save()
    # Get the braintree customer using the id we get from the 
    # create_customer method
    customer = braintree.Customer.find(user.customer_id)
    # Get the first credit card registered to this user.
    # TODO: select credit card using data recieved.
    payment_method_token = customer.credit_cards[0].token
    result = braintree.Subscription.create({
            "payment_method_token": payment_method_token,
            "plan_id": braintree_plan_id
        })
    if result.is_success:
        """
        Again we can store id from here in Subscription model maybe if want to later get it with
        braintree.Subscription.find(id) and get various information from there.
        """
        subscription = Subscription(start_date=datetime.now(), amount_paid=amount,
                                    plan_id=braintree_plan_id, braintree_id=result.subscription.id,
                                    end_date=datetime.now(), date_paid=datetime.now()) # TODO: handle this or just allow null ?
        subscription.save()
        return subscription
    _handle_subscription_failure(result)

    
def _get_basic_transaction_dictionary(amount, card_number, cvv, expiration_month, expiration_year):
    """
    Return the filled dictionary for a basic transaction, with no customer or subscription.
    """
    return {
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
            }
    
    
def _create_simple_transaction(amount, card_number, cvv, expiration_month, expiration_year):
    """
    Create the simplest transaction possible, needing only an amount, card_number, cvv,
     exporation_month, expiration_year.
    """
    transaction_info = _get_basic_transaction_dictionary(amount, card_number, cvv, 
                                                         expiration_month, expiration_year)
    return braintree.Transaction.sale(transaction_info)
    
    
def _create_transaction_for_customer(customer_id, amount, card_number, cvv, expiration_month, 
                                     expiration_year):
    """
    Create a transaction for an existing customer. 
    """
    transaction_info = _get_basic_transaction_dictionary(amount, card_number, cvv, 
                                                         expiration_month, expiration_year)
    transaction_info["customer"] = { "id" : customer_id, }
    transaction_info["options"]["store_in_vault_on_success"] = True
    return braintree.Transaction.sale(transaction_info)


def _create_customer_and_transaction(first_name, last_name, amount, card_number, cvv, 
                                     expiration_month, expiration_year):
    """
    Creates a new customer and a first transaction for that customer.
    """
    transaction_info = _get_basic_transaction_dictionary(amount, card_number, cvv, 
                                                         expiration_month, expiration_year)
    transaction_info["customer"] = { 
                                    "first_name" : first_name, 
                                    "last_name" : last_name,
                                    }
    transaction_info["options"]["store_in_vault_on_success"] = True
    result = braintree.Transaction.sale(transaction_info)
    # If any customer related failures occured, here is where we handle them. Once out
    # only transaction related errors should be unhandled.
    _handle_customer_failure(result)
    return result

def _create_customer(first_name, last_name, card_number, expiration_month, 
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
        return result.customer.id
    _handle_customer_failure(result)


