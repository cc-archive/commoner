from datetime import datetime
import string
import random

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from commoner.util import base62_string

class PromoCodeManager(models.Manager):

    def mark_as_used(self, code, user):
        """ Wrapping repeatedly used lines into a single function,
        employed by user registrations and profile upgrades """
        
        promo = self.get(code__exact=code)
        promo.used_by = user
        promo.used_on = datetime.now()
        promo.save()

        return promo

    def unique_code_string(self):
        """ Generates a random 8 char string from the base62 set. """
        code_string = base62_string(8)

        if self.filter(code = code_string).count() > 0: 
            code_string = self.unique_code_string()

        return code_string
        
    def create_promo_code(self, email=None, trxn_id=None, contrib_id=None,
                          send_email=True):

        """ Manager method that will handle promo code creation triggered
        by the script running on the CiviCRM databse. """

        # need to generate a random code and verify that it is unique
        # rarely will this loop get executed
        promo_code = self.unique_code_string()

        code = self.create(code=promo_code,
                           recipient=(email or ''),
                           transaction_id=trxn_id,
                           contribution_id=contrib_id)

        if send_email and email:
            self.send_invite_letter(code)

        return code
                    
    def send_invite_letter(self, code):

        from django.core.mail import send_mail
        current_site = Site.objects.get_current()
            
        subject = render_to_string('promocodes/email/subject.txt',
                                       { 'site': current_site })
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
            
        message = render_to_string('promocodes/email/welcome.txt',
                                   { 'code':code, 'site': current_site })
            
        result = send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [code.recipient])

        return result
        
class PromoCode(models.Model):

    # the real meat, limiting to 8 char for less ink and confusion
    code = models.CharField(_("code"), max_length=8, primary_key=True, unique=True)
    
    # who the code was originally sent to, might be useful
    recipient = models.EmailField(_("promo code email recipient"), blank=False)
    
    created = models.DateTimeField(_("date created"), auto_now=True)
    expires = models.DateTimeField(_("date expires"), blank=True, null=False)

    # promo codes are created with 2 methods:
    # a contribution at civicrm or by a generic paypal transaction
    
    transaction_id = models.CharField(_("paypal transaction id"),
                                      max_length=255, blank=True, null=True)
    contribution_id = models.CharField(_("CiviCRM invoice id"),
                                       max_length=255, blank=True, null=True)
                                          
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
