import sha
import random

from django.db import models
from django.db.models import permalink
from django.contrib.sites.models import Site

class RegistrationManager(models.Manager):

    def create_registration(self, email, last, first,
                            send_email = True):
        registration = PartialRegistration(
            email = email,
            last_name = last,
            first_name = first)

        registration.save()

        if send_email:
            from django.core.mail import send_mail

            current_site = Site.objects.get_current()
            subject = render_to_string('registration/email/subject.txt',
                                       {'site':current_site})
            message = render_to_string('registration/email/welcome.txt',
                                       {'site':current_site,
                                        'registration':registration})

            send_mail(subect, message, settings.DEFAULT_FROM_EMAIL, [email])

        return registration

class PartialRegistration(models.Model):

    key = models.CharField(max_length=40, primary_key=True,
                           editable=False)

    last_name = models.CharField(max_length=30)
    first_name = models.CharField(max_length=30)
    email = models.EmailField()

    def __unicode__(self):
        return u"%s (%s, %s)" % (
            self.email, self.last_name, self.first_name)

    @permalink
    def get_absolute_url(self):
        return ('commoner.registration.views.complete', (self.key,))

    def save(self):
        # set the SHA-1 hash
        salt = sha.new(str(random.random())).hexdigest()[:5]
        self.key = sha.new(salt+self.email+self.last_name).hexdigest()
        
        # call the real save method
        super(PartialRegistration, self).save()

    objects = RegistrationManager()
