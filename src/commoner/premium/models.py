

from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


class PromoCode(models.Model):
    
    """ 
    
    """

    # the real meat
    code = models.CharField(_("code"), max_length=40, primary_key=True,
                            unique=True, editable=False)
    
    # who the code was originally sent to, might be useful
    recipient = models.EmailField(_("promo code email recipient"), blank=True)
    
    created = models.DateTimeField(_("date created"), default=datetime.now())
    expires = models.DateTimeField(_("date expires"), blank=True, null=False)
    
    transaction_id = models.CharField(_("paypal transaction id"),
                                      max_length=255, blank=True, null=True)
    
    used_by = models.ForeignKey(User, blank=True, null=True)
    used_on = models.DateTimeField(_("date used"), blank=True, null=True)
    
    def __unicode__(self):
        return self.code

    def save(self):
        # if we're creating and the expiration date hasn't been set...
        if not(self.expires):

            # set the expiration to be now + 1 year
            today = datetime.now()
            self.expires = today.replace(today.year + 1)
            
        super(PromoCode, self).save()
