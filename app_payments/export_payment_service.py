'''
This module will hold an API to export from braintree to various sources.
'''
import csv
import braintree
from app_payments.quickbooks_adapters import BraintreeTransactionAdapter

# All available headers for a transaction in IIF format, more details
# on each field can be fount in the IIF Import Kit under IIF Header Help/!Trans.html
# http://support.quickbooks.intuit.com/support/Articles/HOW12778
TRANSACTION_DEFAULT_ORDER = ['TRNSID', 'TRNSTYPE', 'DATE', 'ACCNT', 'NAME', 'AMOUNT',
                           'DOCNUM', 'MEMO', 'CLEAR', 'TOPRINT', 'ADDR1', 'ADDR2',
                           'ADDR3', 'ADDR4', 'ADDR5', 'PAYMETH', 'SADDR1', 'SADDR2', 
                           'SADDR3', 'SADDR4', 'SADDR5']


def quickbooks_export_transactions(transactions_list, output_csv, headers_list=None):
    """
    Export a list of braintree transactions into quickbooks IIF format.
    :param headers_list: optional parameters if we want a different list of headers
    for the IIF result file than the default ones.
    """
    headers_list = headers_list or TRANSACTION_DEFAULT_ORDER
    with open(output_csv, 'w') as csv_file:
        iifwriter = csv.writer(csv_file, delimiter='\t')
        iifwriter.writerow(['!TRNS'] + headers_list)
        iifwriter.writerow(['!ENDTRNS'])
        for trans in transactions_list:
            iifwriter.writerow(['TRNS'] + BraintreeTransactionAdapter(trans).get_row(headers_list))
            iifwriter.writerow(['ENDTRNS'])
    
