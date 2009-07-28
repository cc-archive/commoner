from django import forms
from django.utils.translation import ugettext as _

import models

class PromoCodeField(forms.CharField):
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 40)
        kwargs.setdefault('label', _("Promo code"))
        kwargs.setdefault('required', True)

        super(PromoCodeField, self).__init__(*args, **kwargs)

    def clean(self, value):

        """ Check to see if this Promo Code is valid & hasn't been used """

        if not value and self.required:
            raise forms.ValidationError(_("The promo code is a required field."))
        
        if value:

            try:
                promocode = models.PromoCode.objects.get(code__exact=value)
                
                if promocode.used_by:
                    raise forms.ValidationError(_("This promo code has already been used."))

            except models.PromoCode.DoesNotExist:
                raise forms.ValidationError(_("The promo code entered is invalid."))

        return value
