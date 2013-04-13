"""
An API to braintree to provide specific queries we would like.
"""
import datetime
import braintree


def get_transactions_before(input_date=None):
    """
    Get all transactions that occured before supplied parameter :input_date:
    """
    input_date = input_date or datetime.datetime.now()
    all_sales = braintree.Transaction.search(
        braintree.TransactionSearch.created_at.less_than_or_equal_to(input_date),
    )
    return all_sales.items


def get_transactions_in_date_inverval(start_date, end_date):
    """
    Get all transcation that occured in given interval.
    """
    all_sales = braintree.Transaction.search(
        braintree.TransactionSearch.created_at.between(start_date, end_date),
    )
    return all_sales.items


def get_transactions_with_amount_range(min_amount, max_amount):
    """
    Get all transcation that occured in given interval.
    """
    all_sales = braintree.Transaction.search(
        braintree.TransactionSearch.amount.between(str(min_amount), str(max_amount)),
    )
    return all_sales.items

