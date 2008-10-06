from datetime import datetime

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
    created = models.DateTimeField(default = datetime.now())
    updated = models.DateTimeField()

    def __unicode__(self):
        return u"%s - %s" % (self.owner, self.created)

    def save(self):
        # set the updated timestamp
        self.updated = datetime.now()

        super(Registration, self).save()

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
    license_url = models.URLField(max_length=255, blank=True,
                              help_text="The URL of the license your work is available under.")

    registered = models.DateTimeField(default=datetime.now())
    updated = models.DateTimeField()

    same_as = models.ForeignKey("self", blank=True, null=True)

    def get_absolute_url(self):
        return reverse('view_work', args=(self.id,))

    def __unicode__(self):
        return self.title or self.url

    def save(self):
        # set the updated timestamp
        self.updated = datetime.now()

        super(Work, self).save()

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
