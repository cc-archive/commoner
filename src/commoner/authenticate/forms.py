from django import forms
from django.contrib import auth

from django.utils.translation import ugettext_lazy as _

class LoginForm(auth.forms.AuthenticationForm):

    remember = forms.BooleanField(label=_(u"Remember me"),
                                  required=False)
