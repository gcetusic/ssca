"""
Any braintree entity to which we want to have a quickbooks equivalent
and needs some complex mappings should have an adapter here that should
expose at the least a get_value(header_key) and get_row(headers_list) methods.
"""
from abc import ABCMeta, abstractmethod
import braintree

class ABCAdapter():
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def get_value(self, header_key):
        """
        Any adapter should know, given a QuickBooks specific header_key as
        parameter return the braintree best equivalent of that.
        """
        pass
    
    
    @abstractmethod
    def get_row(self, headers_list):
        """
        Any adapter should know, given a QuickBooks specific header_list as
        parameter, to return the corresponding data from a braintree instace.
        """
        pass
    

class BraintreeTransactionAdapter():
    """
    An adapter for a braintree transaction for easy adaptation to
    quickbooks specific format.
    """
    def __init__(self, btree_trans):
        self._btree_transaction = btree_trans
    
        
    def get_value(self, header_key):
        """
        For a given QuickBooks specific header_key return as best as possible
        the equivalent from a braintree transaction.
        """
        if header_key == 'TRNSID':
            return self._btree_transaction.id
        elif header_key == 'TRNSTYPE':
            return self.get_transaction_type()
        elif header_key == 'DATE':
            return self._btree_transaction.created_at.strftime('%m/%d/%y')
        elif header_key == 'ACCNT':
            return self._btree_transaction.merchant_account_id
        elif header_key == 'NAME':
            return self.get_customer_name()
        elif header_key == 'AMOUNT':
            return float(self._btree_transaction.amount)
        elif header_key == 'DOCNUM':
            return self._btree_transaction.order_id
        elif header_key == 'MEMO':
            # No equivalent from what I can see. TODO: Remove it entirely?
            return ''
        elif header_key == 'CLEAR':
            return self.get_cleared_status()
        elif header_key == 'TOPRINT':
            # Again no equiavalent. TODO: Remove it entirely?
            return 'N'
        elif header_key == "ADDR1":
            return self.get_billing_address()
        elif header_key in ("ADDR2", "ADDR3", "ADDR4", "ADDR5"):
            # TODO: check here how long can the address be and if 
            # needed split result from 'ADDR1' into all these 5
            return ""
        elif header_key == 'PAYMETH':
            return self._btree_transaction.credit_card['card_type']
        elif header_key == 'SADDR1':
            return self.get_shipping_address()
        elif header_key in ("SADDR2", "SADDR3", "SADDR4", "SADDR5"):
            # TODO: Same as for ADDR above
            return ""
        return "Unknown"
        
        
    def get_row(self, headers_list):
        """
        Just get value for each entry in header list and return result.
        """
        return [self.get_value(header_key) for header_key in headers_list]
    
        
    def get_transaction_type(self):
        '''
        Braintree classifies transactions in one of two types, sale or credit 
        while quickbooks has a range of possible transaction types. Just do a
        mapping as best we can here.
        '''
        if self._btree_transaction.type == braintree.Transaction.Type.Credit:
            return 'CREDIT CARD'
        elif self._btree_transaction.type == braintree.Transaction.Type.Sale:
            return 'PURCHORD'
        
        
    def get_customer_name(self):
        """
        If transaction has a customer associated with it return it's name else
        return unknown.
        """
        if self._btree_transaction.customer['first_name']:
            return ' '.join([self._btree_transaction.customer['first_name'], 
                             self._btree_transaction.customer['last_name']])
        else:
            return 'Unknown'
        
        
    def get_cleared_status(self):
        """
        Any other status than settlet and let's just consider the transaction
        as not clear.
        """
        if self._btree_transaction.status == 'settled':
            return 'Y'
        else:
            return 'N'
       
        
    def get_billing_address(self):
        """
        See if any billing details are present, otherwise return unknown.
        """
        if self._btree_transaction.billing_details.street_address:
            street = self._btree_transaction.billing_details.street_address
            postal_code = self._btree_transaction.billing_details.street_address
            country_code = self._btree_transaction.billing_details.country_code_alpha2
            return ','.join([street, postal_code, country_code])
        else:
            return 'Unknown'
        
        
    def get_shipping_address(self):
        """
        See if any shipping details are present, otherwise return unknown.
        """
        if self._btree_transaction.shipping_details.street_address:
            street = self._btree_transaction.shipping_details.street_address
            postal_code = self._btree_transaction.shipping_details.street_address
            country_code = self._btree_transaction.shipping_details.country_code_alpha2
            return ','.join([street, postal_code, country_code])
        else:
            return 'Unknown'
        
        
    def __repr__(self):
        return str(self._btree_transaction)
    
    
    def __str__(self):
        return str(self._btree_transaction)
    
    