from django import forms
from django.utils.translation import ugettext_lazy as _

class ContactForm(forms.Form):

    sender = forms.EmailField(label=_(u"Email address"))
    subject = forms.CharField(label=_(u"Message subject"))
    message = forms.CharField(label=_(u"Message"),
                              widget=forms.Textarea)

