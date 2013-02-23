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

    # string constants to be used in templates
    loc_usa = 'in the United States'
    loc_canada = 'in Canada or Mexico'
    loc_overseas = 'Overseas (surface mail)'
    send_first_class = 'Send via First Class Mail (Add $5)'
    send_international = 'Send via International Airmail (Add $15)'

    mail_locations = [('5', loc_usa),
            ('15', loc_canada),
            ('15', loc_overseas)]

    burgee_types = [('25', 'Large (18" x 24")'),
            ('25', 'Medium (12" x 18")'),
            ('17', 'Small (10" x 15")')]

    # validation parameters to be used in js
    min_firstname = 5
    min_lastname = 5

    # fields for step 1 dialog
    firstname = forms.CharField(max_length=32, required = True,
            widget=forms.TextInput( attrs={'placeholder': 'First Name','class': 'input-xlarge'}))

    lastname = forms.CharField(max_length=32, required = True,
            widget=forms.TextInput( attrs={'placeholder': 'Last Name','class': 'input-xlarge'}))

    email = forms.EmailField(required = True,
            widget=forms.TextInput( attrs={'placeholder': 'Email Address','class': 'input-xlarge'}))

    # fields for step 2 dialog
    membership_fee = forms.IntegerField()

    mail_location = forms.ChoiceField(choices = mail_locations,
            widget=forms.Select(attrs={'onchange':'onMailLocationChange();'}))

    # fields for step 3 dialog
    burgee_type = forms.ChoiceField(choices = burgee_types,
            widget=forms.Select(attrs={'onchange':'onBurgeeChanged();'}))

    name_on_card = forms.CharField(max_length=32, required = True,
            widget=forms.TextInput( attrs={'placeholder': 'Full Name','class': 'input-xlarge'}))

    card_type = forms.ChoiceField(required = True, 
            widget = forms.Select(), choices = card_types)

    card_number = forms.CharField(max_length=32, required = True,
            widget=forms.TextInput( attrs={'placeholder': '14-digit number','class': 'input-xlarge'}))

    card_expiry_date = forms.DateField(required = True)

    card_csv = forms.CharField(max_length=3, required = True,
            widget=forms.TextInput(attrs={'style': 'width: 40px;', 'class': 'input-xlarge'}))

    total_fee = forms.IntegerField() 
    yearly_reniew = forms.BooleanField() 
