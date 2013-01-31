from django import forms

class SSCAJoinForm(forms.Form):
    """
    SSCA Join Form defines fields to be used in Join SSCA js popups.
    """

    card_types = [('Visa', 'Visa'), 
            ('MasterCard', 'MasterCard'),
            ('American Express', 'American Express'),
            ('Discover', 'Discover'),
            ('Diners Club', 'Diners Club'),
            ('JCB', 'JCB')]

    # for step 1 dialog
    firstname = forms.CharField(max_length=32, widget=forms.TextInput(
        attrs={'placeholder': 'First Name'}))
    lastname = forms.CharField(max_length=32, widget=forms.TextInput(
        attrs={'placeholder': 'Last Name'}))
    email = forms.EmailField( widget=forms.TextInput(
        attrs={'placeholder': 'Email Address'}))

    # for step 2 dialog
    membership_fee = forms.IntegerField()

    # for step 3 dialog
    name_on_card = forms.CharField(max_length=32)
    card_type = forms.ChoiceField(widget = forms.Select(), choices = card_types, required = True,)
    card_number = forms.CharField(max_length=32)
    card_expiry_date = forms.DateField()
    card_csv = forms.CharField(max_length=3)
    total_fee = forms.IntegerField() 
    yearly_reniew = forms.BooleanField() 
