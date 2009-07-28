import re
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from django import forms

from commoner.premium.models import PromoCode
from commoner.premium.forms import PromoCodeField

from models import RESERVED_NAMES, Registration

class RegistrationForm(forms.Form):    
    
    first_name = forms.CharField(label=_(u"First name"), max_length=30)
    last_name = forms.CharField(label=_(u"Last name"), max_length=30)
    email = forms.EmailField(label=_(u"Email address"))
    
    username = forms.CharField(label=_(u"Username"), max_length=30,
                               help_text="https://creativecommons.net/USERNAME")
    password1 = forms.CharField(label=_(u"Password"),
                                widget=forms.PasswordInput)
    password2 = forms.CharField(label=_(u"Password (again)"),
                                widget=forms.PasswordInput)
    agree_to_tos = forms.BooleanField(label=_(u"I have read and agreed "
                                       "to the Terms of Use."),
                                       widget=forms.CheckboxInput,
                                       help_text=_(u"By agreeing to the Terms of Use you affirm you are at least 13 years of age.  If you are between 13 years old and the age of majority in your jurisdiction, you affirm that you have obtained your parent's or legal guardian's express permission to create an account as required by CC."),
				       error_messages = dict(
				       required=_(u'You must read and agree to the Terms of Use.'),
				       ))
    
    promo_code = PromoCodeField(required=False)
    
    RE_ALNUM = re.compile(r'^\w+$')

    def clean_username(self):
        """
        Validate that the username is alphanumeric and is not already
        in use.
        """
        
        # usernames must be at least two characters long
        if len(self.cleaned_data['username']) < 2:
            raise forms.ValidationError(_(u'Usernames must be at least two characters long.'))

        # usernames can only contain letters, numbers and underscores
        if not self.RE_ALNUM.search(self.cleaned_data['username']):
            raise forms.ValidationError(_(u'Usernames can only contain letters, numbers and underscores.'))

        # usernames can not be a reserved value
        if self.cleaned_data['username'] in RESERVED_NAMES:
            raise forms.ValidationError(_(u'This username is already taken. Please choose another.'))
            
        # make sure this user does not exist
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
        
        if 'password1' in self.cleaned_data and \
                'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_(u'You must type the same password each time'))
        
        return self.cleaned_data

    def save(self):
        
        # create the Registration
        registration = Registration.objects.create_registration(
            self.cleaned_data['username'],
            self.cleaned_data['email'],
            self.cleaned_data['first_name'],
            self.cleaned_data['last_name'],
            self.cleaned_data['password1'],
            self.cleaned_data['promo_code']
        )

        """
        # update `PromotionCode` as 'used'
        if self.cleaned_data['promo_code']:
            promo = PromotionCode.objects.get(code__exact=self.cleaned_data['promo_code'])
            promo.used_by = registration.user
            promo.save()
        """

        return registration
