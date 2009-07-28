import sha
import random
from datetime import datetime

from django.conf import settings
from django.db import models
from django.dispatch import Signal
from django.template.loader import render_to_string
from django.db.models import permalink
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from commoner.premium.models import PromoCode
from commoner.profiles.models import CommonerProfile

RESERVED_NAMES = ('admin', 'pony')

registration_activated = Signal(providing_args=["registration"])

class RegistrationManager(models.Manager):

    def send_activation_email(self, registration):
        """ Send the activation email for a registration. """

        from django.core.mail import send_mail

        current_site = Site.objects.get_current()
        subject = render_to_string('registration/email/subject.txt',
                                   {'site':current_site}).strip()
        message = render_to_string('registration/email/welcome.txt',
                                   {'site':current_site,
                                    'registration':registration})

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, 
                  [registration.user.email])

    def create_registration(self, username, email, first_name, last_name,
                            password, promo_code, send_email=True):

        """ Create a `User` for the user, but set the active field to false
        to force the user to activate before being able to login. """
        
        # Generate a new user, uses create_user to handle password hashing
        user = User.objects.create_user(username, email, password)
        user.first_name = first_name
        user.last_name = last_name
        user.is_active = False
        user.save()
        
        registration = Registration(user=user, promo_code=promo_code)
        registration.save()

        if send_email:
            self.send_activation_email(registration)

        return registration

    def activate_user(self, activation_key):

        """ Activates the `User` for the `Registration` object paired to
        the activation_key.  Returns the `User` instance if the key was
        valid. """

        try:
            registration = Registration.objects.get(key__exact=activation_key)

        except Registration.DoesNotExist:
            return None

        user = registration.user
        user.is_active = True
        user.save()

        # create a profile for them
        profile = CommonerProfile(user=user)

        # the code was validated by the form
        if registration.promo_code:        
            profile.level = CommonerProfile.PREMIUM

        profile.save()
                    
        return user

class Registration(models.Model):
    
    """ Holds a reference to a user and the string that must be used to activate
    the account.
    `transaction_id` is a legacy reference to the id number of the Paypal transaction
    that spawned the registration """
    
    key = models.CharField(max_length=40, primary_key=True,
                           editable=False)

    # need a place to store the promo code used on the registration form
    promo_code = models.CharField(max_length=40, blank=True)
    
    user = models.ForeignKey(User, blank=True, null=True, related_name="registration")
    
    def __unicode__(self):
        return u"%s (%s, %s)" % (
            self.email, self.last_name, self.first_name)

    @permalink
    def get_absolute_url(self):
        return ('commoner.registration.views.activate', (self.key,))

    def save(self):

        # see if we already have a key
        if not(self.key):
            # set the SHA-1 hash
            salt = sha.new(str(random.random())).hexdigest()[:5]
            self.key = sha.new(salt+self.user.email+self.user.last_name).hexdigest()
                
        # call the real save method
        super(Registration, self).save()

    objects = RegistrationManager()

    class Meta:
        verbose_name=_("user registration")
