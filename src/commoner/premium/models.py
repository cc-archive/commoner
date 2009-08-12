from datetime import datetime
import string
import random

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

# promo codes are case sensitive alpha-numeric strings
BASE62 = string.letters + string.digits

class PromoCodeManager(models.Manager):

    def mark_as_used(self, code, user):
        """ Wrapping repeatedly used lines into a single function,
        employed by user registrations and profile upgrades """
        
        promo = self.get(code__exact=code)
        promo.used_by = user
        promo.used_on = datetime.now()
        promo.save()

        return promo

class PromoCode(models.Model):
    
    """ 
    TODO decide that you are fine with this module and document it
    """

    # the real meat, limiting to 8 char for less ink and confusion
    code = models.CharField(_("code"), max_length=8, primary_key=True,
                            unique=True, editable=False)
    
    # who the code was originally sent to, might be useful
    recipient = models.EmailField(_("promo code email recipient"), blank=True)
    
    created = models.DateTimeField(_("date created"), default=datetime.now())
    expires = models.DateTimeField(_("date expires"), blank=True, null=False)
    
    transaction_id = models.CharField(_("paypal transaction id"),
                                      max_length=255, blank=True, null=True)
    
    used_by = models.ForeignKey(User, blank=True, null=True)
    used_on = models.DateTimeField(_("date used"), blank=True, null=True)

    objects = PromoCodeManager()
    
    def __unicode__(self):
        return self.code

    def gencode(self):
        """ Generates a random 8 char string from the base62 set. """
        return ''.join([random.choice(BASE62) for i in range(0,8)])

    @property
    def used(self):
        """ Returns True if the code has been used """
        return self.used_by is not None
        
    def save(self):

        # if we're creating and the expiration date hasn't been set...
        if not(self.expires):

            # set the expiration to be now + 1 year
            today = datetime.now()
            self.expires = today.replace(today.year + 1)

        if not(self.code):

            # create a unique code
            self.code = self.gencode()
        
        super(PromoCode, self).save()
