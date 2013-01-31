from django import forms

class SSCAJoinForm(forms.Form):
    """
    SSCA Join Form defines fields to be used in Join SSCA js popups.
    """
    card_types = [('Visa', 'Visa'), ('MasterCard', 'MasterCard'),
            ('American Express', 'American Express'),
            ('Discover', 'Discover'),
            ('Diners Club', 'Diners Club'),
            ('JCB', 'JCB')]

    mail_locations = [('5', 'in the United States'),
            ('15', 'in Canada or Mexico'),
            ('15', 'Overseas (surface mail)')]

    burgee_types = [('25', 'Large (18" x 24")'),
            ('25', 'Medium (12" x 18")'),
            ('17', 'Small (10" x 15")')]

    # fields for step 1 dialog
    firstname = forms.CharField(max_length=32, required = True,
            widget=forms.TextInput( attrs={'placeholder': 'First Name'}))

    lastname = forms.CharField(max_length=32, required = True,
            widget=forms.TextInput( attrs={'placeholder': 'Last Name'}))

    email = forms.EmailField(required = True,
            widget=forms.TextInput( attrs={'placeholder': 'Email Address'}))

    # fields for step 2 dialog
    membership_fee = forms.IntegerField()

    mail_location = forms.ChoiceField(choices = mail_locations,
            widget=forms.Select(attrs={'onchange':'updateTotal();'}))

    # fields for step 3 dialog
    burgee_type = forms.ChoiceField(choices = burgee_types,
            widget=forms.Select(attrs={'onchange':'updateSSCAPurchase();'}))

    name_on_card = forms.CharField(max_length=32, required = True)

    card_type = forms.ChoiceField(required = True, 
            widget = forms.Select(), choices = card_types)

    card_number = forms.CharField(max_length=32, required = True)
    card_expiry_date = forms.DateField(required = True)
    card_csv = forms.CharField(max_length=3, required = True)
    total_fee = forms.IntegerField() 
    yearly_reniew = forms.BooleanField() 
