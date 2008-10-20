import sha
import urlparse

from django import forms
from django.conf import settings
from django.contrib import auth

from django.utils.translation import ugettext_lazy as _

def make_secret(value):

    salt = sha.new(settings.SECRET_KEY).hexdigest()[:5]
    return sha.new(salt+value).hexdigest()

class OpenIdLoginForm(forms.Form):

    password = forms.CharField(label=_(u"Password"),
                               widget=forms.PasswordInput())
    secret = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, id_url, **kwargs):

        self.id = id_url
        self.username = urlparse.urlsplit(id_url)[2][1:-1]

        super(OpenIdLoginForm, self).__init__(**kwargs)

    def clean_password(self):
        password = self.cleaned_data['password']

        user = auth.authenticate(username=self.username, 
                                 password=password)
        if not user:
            raise forms.ValidationError(_(u"Incorrect password."))

    def clean(self):
        """Verify the secret matches."""

        if self.cleaned_data['secret'] != make_secret(self.id):
            raise AssertionError()

        return self.cleaned_data
