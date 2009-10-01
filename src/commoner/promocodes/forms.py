from django import forms
from django.utils.translation import ugettext as _

import models

class PromoCodeField(forms.CharField):

    errors = {
        'already_used' : _("This authorization code has already been used."),
        'invalid_code' : _("The authorization code entered is invalid."),
        'required' : _("The authorization code is a required field."),
    }
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 8)
        kwargs.setdefault('label', _("Authorization code"))
        kwargs.setdefault('required', True)
        kwargs.setdefault('help_text', _('Your authorization code is in your receipt of payment to Creative Commons.'))

        super(PromoCodeField, self).__init__(*args, **kwargs)

    def clean(self, value):

        """ Check to see if this Authorization Code is valid & hasn't been used """

        if not value and self.required:
            raise forms.ValidationError(self.errors['required'])
        
        if value:

            try:
                promocode = models.PromoCode.objects.get(code__exact=value)
                
                if promocode.used_by:
                    raise forms.ValidationError(self.errors['already_used'])

            except models.PromoCode.DoesNotExist:
                raise forms.ValidationError(self.errors['invalid_code'])

        return value

class PremiumUpgradeForm(forms.Form):

    promo = PromoCodeField()

    def save(self):
        """
        When the form is save the promo code object is returned
        Arguments:
        - `self`:
        """

        promo_code = models.PromoCode.objects.get(
            code__exact=self.cleaned_data['promo'])

        return promo_code
        
        

        
