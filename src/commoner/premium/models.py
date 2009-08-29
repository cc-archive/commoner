from datetime import datetime
import string
import random

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
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

    def gencode(self):
        """ Generates a random 8 char string from the base62 set. """
        return ''.join([random.choice(BASE62) for i in range(0,8)])

    def create_promo_code(self, email=None, trxn_id=None, contrib_id=None,
                          send_email=True):

        """ Manager method that will handle promo code creation triggered
        by the script running on the CiviCRM databse. """

        # need to generate a random code and verify that it is unique
        # rarely will this loop get executed
        promo_code = self.gencode()
        
        # catching an IntegrityError would save a db hit, but importing
        # the exception is db_engine specific and complicates testing env
        while self.filter(code = promo_code).count() > 0: # db hit
            # code has already been used, create another
            promo_code = self.gencode()

        code = self.create(code=promo_code,
                           recipient=email,
                           transaction_id=trxn_id,
                           contribution_id=contrib_id)

        if send_email and email:

            from django.core.mail import send_mail
            current_site = Site.objects.get_current()
            
            subject = render_to_string('premium/email/subject.txt',
                                       { 'site': current_site })
            # Email subject *must not* contain newlines
            subject = ''.join(subject.splitlines())
            
            message = render_to_string('premium/email/welcome.txt',
                                       { 'code':code, 'site': current_site })
            
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

        return code
                    
        

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

    # promo codes are created with 2 methods:
    # a contribution at civicrm or by a generic paypal transaction
    
    transaction_id = models.CharField(_("paypal transaction id"),
                                      max_length=255, blank=True, null=True)
    contribution_id = models.IntegerField(_("CiviCRM contribution id"),
                                          blank=True, null=True)
                                          
    used_by = models.ForeignKey(User, blank=True, null=True)
    used_on = models.DateTimeField(_("date used"), blank=True, null=True)

    objects = PromoCodeManager()
    
    def __unicode__(self):
        return self.code

    @property
    def used(self):
        """ Returns True if the code has been used """
        return self.used_by is not None
        
    def save(self, *args, **kwargs):

        # if we're creating and the expiration date hasn't been set...
        if not(self.expires):

            # set the expiration to be now + 1 year
            today = datetime.now()
            self.expires = today.replace(today.year + 1)

        super(PromoCode, self).save(*args, **kwargs)
