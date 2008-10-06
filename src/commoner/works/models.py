from django.db import models

from django.db import models
from django.db.models import permalink
from django.core.urlresolvers import reverse

from commoner.util import getBaseURL

from commoner.profiles.models import CommonerProfile
from django.contrib.auth.models import User

class Registration(models.Model):

    owner = models.ForeignKey(User, 
                              related_name='registrations')
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

class Feed(Registration):

    url = models.URLField(max_length=255, blank=False, verify_exists=False)
    license = models.URLField(max_length=255, blank=True)    


class Work(models.Model):

    registration = models.ForeignKey(Registration,
                                     related_name='works')

    url = models.URLField(max_length=255, blank=False,
                          verify_exists=False,
                          verbose_name="Work URL")

    title = models.CharField(max_length=255, blank=True)
    registered = models.DateField(auto_now_add=True)
    license_url = models.URLField(max_length=255, blank=True,
                              help_text="The URL of the license your work is available under.")
    same_as = models.ForeignKey("self", blank=True, null=True)

    def get_absolute_url(self):
        return reverse('view_work', args=(self.id,))

    def __unicode__(self):
        return self.title or self.url

    @property
    def owner(self):
        return self.registration.owner

    @property
    def license(self):
        """Return the license name for the specified URL; 
        fall back to the URL."""

        return self.license_url

class Glob(Work):
    
    pattern = models.CharField(max_length=255, blank=True)
