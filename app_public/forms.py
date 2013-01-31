from django import forms

class SSCAJoinForm(forms.Form):
    """
    SSCA Join Form defines fields to be used in Join SSCA js popups.
    """
    # for step 1 dialog
    firstname = forms.CharField(max_length=32)
    lastname = forms.CharField(max_length=32)
    email = forms.EmailField()

    # for step 2 dialog
    membership_fee = forms.IntegerField()

    # for step 3 dialog
    name_on_card = forms.CharField(max_length=32)
    card_type = forms.CharField(max_length=32)
    card_number = forms.CharField(max_length=32)
    card_expiry_date = forms.DateField()
    card_csv = forms.CharField(max_length=3)
    total_fee = forms.IntegerField() 
    yearly_reniew = forms.BooleanField() 
