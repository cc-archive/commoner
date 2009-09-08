"""
Forms and validation code for user registration.

"""


from django.contrib.auth.models import User
from django import forms
from django.utils.translation import ugettext_lazy as _

from models import RegistrationProfile

from commoner.promocodes.forms import PromoCodeField

# I put this on all required fields, because it's easier to pick up
# on them with CSS or JavaScript if they have a class of "required"
# in the HTML. Your mileage may vary. If/when Django ticket #3515
# lands in trunk, this will no longer be necessary.
attrs_dict = { 'class': 'required' }

class BaseRegistrationForm(forms.Form):
    """
    Form for registering a new user account.
    
    Validates that the requested username is not already in use, and
    requires the password to be entered twice to catch typos.
    
    Subclasses should feel free to add any additional validation they
    need, but should either preserve the base ``save()`` or implement
    a ``save()`` method which returns a ``User``.
    
    """
    username = forms.RegexField(regex=r'^\w+$',
                                max_length=30,
                                widget=forms.TextInput(attrs=attrs_dict),
                                label=_(u'Username'))
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict,
                                                               maxlength=75)),
                             label=_(u'Email address'))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
                                label=_(u'Password'))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
                                label=_(u'Password (again)'))
    
    def clean_username(self):
        """
        Validate that the username is alphanumeric and is not already
        in use.
        
        """
        try:
            user = User.objects.get(username__iexact=self.cleaned_data['username'])
        except User.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError(_(u'This username is already taken. Please choose another.'))

    def clean(self):
        """
        Verifiy that the values entered into the two password fields
        match. Note that an error here will end up in
        ``non_field_errors()`` because it doesn't apply to a single
        field.
        
        """
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_(u'You must type the same password each time'))
        return self.cleaned_data
    
    def save(self):
        """
        Create the new ``User`` and ``RegistrationProfile``, and
        returns the ``User`` (by calling
        ``RegistrationProfile.objects.create_inactive_user()``).
        
        """
        new_user = RegistrationProfile.objects.create_inactive_user(username=self.cleaned_data['username'],
                                                                    password=self.cleaned_data['password1'],
                                                                    email=self.cleaned_data['email'])
        return new_user


class RegistrationForm(BaseRegistrationForm):
    """
    Subclass of ``BaseRegistrationForm`` which adds a required checkbox
    for agreeing to CC.net's  Terms of Service.

    This form also requires users to enter their First and Last names

    The promo code field is optional, if the user enters a code, the code will
    be checked to determine that a record for it exists in the database.  If
    so, the code is marked as used and the user is added to the premium group.
        
    """
    agree_to_tos = forms.BooleanField(widget=forms.CheckboxInput(attrs=attrs_dict),
                             label=_(u"By agreeing to the Terms of Use you affirm you are at least 13 years of age.  If you are between 13 years old and the age of majority in your jurisdiction, you affirm that you have obtained your parent's or legal guardian's express permission to create an account as required by CC."),
                             error_messages={ 'required': u"You must agree to the terms to register" })
    
    promo_code = PromoCodeField()

    def save(self):
        """
        Create the new ``User`` and ``RegistrationProfile``, and
        returns the ``User`` (by calling
        ``RegistrationProfile.objects.create_inactive_user()``).

        Overload the parent's save() to handle first & last names
        
        """
        new_user = RegistrationProfile.objects.create_inactive_user(username=self.cleaned_data['username'],
                                                                    password=self.cleaned_data['password1'],
                                                                    email=self.cleaned_data['email'],
                                                                    promo=self.cleaned_data['promo_code'])

        
        return new_user
    
    
