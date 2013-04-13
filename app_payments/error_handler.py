'''
This module holds helper methods for specific braintree operations and make sure they 
handle them appropriately in ssca context.
A full list of error codes can be found at:
    https://www.braintreepayments.com/docs/python/{$$TYPE$$}/validations
    
where $$TYPE$$ is the type of operation attempted, eg. transcations, subscriptions, customers
'''
from app_payments.exceptions import *

def _handle_subscription_failure(braintree_result):
    """
    Handle failure for subscription operations. Just take the first error and treat that code.
    List of all codes at:
        https://www.braintreepayments.com/docs/python/subscriptions/validations
    """
    if braintree_result.is_success:
        # Why are we here at all! Let's return
        return
    if braintree_result.errors.for_object('subscription').size <= 0:
        # We have errors but we are probably calling the wrong method.
        msg = """ Braintree operation has failed, but there are no subscription related errors.
                  Possible to have some unhandled transaction or customer related errors."""
        raise BasePaymentException(msg)
    error_code = braintree_result.errors.for_object('subscription')[0].code
    if error_code == "91904":
        # Invalid plan id.
        msg = """ You have attempted to create a subscription with an invalid braintree plan ID.
                  The plan must be created on braintree in order to be used for a subscription.
                 """
        raise InvalidSubscriptionId(msg)
    elif error_code == "91903":
        # Payment token used for subscripion is invalid.
        msg = """ The credit card token used for the subscription appears to be invalid. """
        raise InvalidPaymentToken(msg)
    msg = """ Subscription failed for some unhandled reason. Error code: %s """ %(error_code,)
    raise BaseSubscriptionException(msg)


def _handle_customer_failure(braintree_result):
    """
    Handle failure for customer operations. Just take the first error and treat that code.
    List of all codes at:
        https://www.braintreepayments.com/docs/python/customers/validations
    """
    if braintree_result.is_success:
        # Why are we here at all! Let's return
        return
    if len(braintree_result.errors.deep_errors) <= 0:
        # We have errors not customer related ones.
        msg = """ Braintree operation has failed, but there are no customer related errors. """
        raise BaseCustomerException(msg)
    error_code = braintree_result.errors.deep_errors[-1].code
    if error_code ==  "81608":
        # First name is too long. Max 255 chars.
        msg = "Customer first name is invalid. Should be a maximum of 255 characters."
        raise InvalidCustomerData(msg)
    elif error_code == "81613":
        # Last name is too long. Max 255 chars.
        msg = "Customer last name is invalid. Should be a maximum of 255 characters."
        raise InvalidCustomerData(msg)
    # We have no code for customer register, fallback to transaction handling.
    _handle_transaction_failure(braintree_result)
        

def _handle_transaction_failure(braintree_result):
    '''
    Handle failures on braintree transaction.
    '''
    if braintree_result.is_success:
        # Why are we here at all! Let's return
        return
    if not braintree_result.transaction:
        if len(braintree_result.errors.deep_errors) <= 0:
            # We have errors but we are probably calling the wrong method.
            msg = """ Braintree operation has failed, but there are no transaction related errors. """
            raise BaseTransactionException(msg)
        error_code = braintree_result.errors.deep_errors[-1].code
        if error_code == "81715":
            # Credit card is not supported by provider..
            msg = "The credid card you provided is not supported by provide.."
            raise InvalidTransactionParameters(msg)
        msg = """ Transaction failed for some unhandled reason. Error code: %s """ %(error_code,)
        raise BasePaymentException(msg)
    elif braintree_result.transaction.status == "processor_declined":
        # Processor declined for some reason e.g. lack of funds
        raise ProcessorDeclinedPayment(braintree_result.transaction.processor_response_text)
    elif braintree_result.transaction.status == "gateway_rejected":
        # Gateway refused transaction for some reasone e.g. invalid cvv
        raise GatewayDeclinedPayment(braintree_result.transaction.gateway_rejection_reason)
    else:
        raise BasePaymentException("Transaction was refused. Make sure you entered valid data.")



