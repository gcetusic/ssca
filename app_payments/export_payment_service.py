'''
This module will hold an API to export from braintree to various sources.
'''
import braintree

def _get_all_transactions():
    result = []
    all_sales = braintree.Transaction.search(
        braintree.TransactionSearch.type == "sale",
    )
    for sale in all_sales.items:
        sale_dict_repr = {}
        for attr in dir(sale):
            if not attr.startswith('_'):
                try:
                    sale_dict_repr[attr] = getattr(sale, attr)
                except Exception, ex:
                    print ex #TODO: use some logging?
                    sale_dict_repr[attr] = "unknown"
        result.append(sale_dict_repr)
    return result
    
