class BasePaymentException(Exception):
    pass

class InvalidTransactionParameters(BasePaymentException):
    pass

class ProcessorDeclinedPayment(BasePaymentException):
    pass

class GatewayDeclinedPayment(BasePaymentException):
    pass

class BaseSubscriptionException(BasePaymentException):
    pass