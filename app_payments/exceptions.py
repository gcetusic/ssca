class BasePaymentException(Exception):
    """
    Base exception class for all payment related operations.
    """
    pass

class BaseTransactionException(BasePaymentException):
    """
    Base exception class for all transaction operations.
    """
    pass

class InvalidTransactionParameters(BasePaymentException):
    """
    Exception to be raised in case some invalid parameters are passed to a transaction.
    """
    pass

class ProcessorDeclinedPayment(BasePaymentException):
    """
    Exception to be raised in case a processor declines our payments for some reason.
    """
    pass

class GatewayDeclinedPayment(BasePaymentException):
    """
    Exception to be raised if a gateway declines our payments for some reason.
    """
    pass

class BaseCustomerException(BasePaymentException):
    """
    Base exception class for all customer operations.
    """
    pass

class InvalidCustomerData(BaseCustomerException):
    """
    Exception to be raised in case some customer related data is invalid.
    """
    pass

class BaseSubscriptionException(BasePaymentException):
    """
    Base exception class for all subscription operations.
    """
    pass

class InvalidSubscriptionId(BaseSubscriptionException):
    """
    Exception to be raised in case an invalid plan id is passed to a subscription.
    """
    pass

class InvalidPaymentToken(BaseSubscriptionException):
    """
    Exception to be raised in case an invalid payment token is passed to a subscription.
    """
    pass
