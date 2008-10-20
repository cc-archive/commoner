import sha
import sha

from django import forms
from django.conf import settings
from django.contrib import auth

from django.utils.translation import ugettext_lazy as _

def make_secret(value):

    salt = sha.new(settings.SECRET_KEY).hexdigest()[:5]
    return sha.new(salt+value).hexdigest()

class OpenIdLoginForm(forms.Form):

    username = forms.CharField(label=_(u"Username"))
    password = forms.CharField(label=_(u"Password"),
                               widget=forms.PasswordInput())
    secret = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, id_url, **kwargs):

        self.id = id_url

        super(OpenIdLoginForm, self).__init__(**kwargs)

    def clean(self):
        """Verify the secret matches."""

        user = auth.authenticate(username=self.cleaned_data['username'], 
                                 password=self.cleaned_data['password'])
        if not user:
            raise forms.ValidationError(_(u"Incorrect password."))

        
        if self.cleaned_data['secret'] != make_secret(self.id):
            raise AssertionError()

        return self.cleaned_data
