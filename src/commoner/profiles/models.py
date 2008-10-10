import os.path
import urlparse

from datetime import datetime

from django.db import models
from django.db.models import permalink
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from commoner.util import getBaseURL

class CommonerProfile(models.Model):
    
    user = models.ForeignKey(User, unique=True)

    nickname = models.CharField(_("Screen name"), max_length=255, blank=True)
    photo = models.ImageField(_("Photo"), upload_to='user/p', blank=True, null=True)

    homepage = models.URLField(_("Homepage"), max_length=255, blank=True)
    location = models.CharField(_("Location"), max_length=255, blank=True)

    story = models.TextField(blank=True)

    created = models.DateTimeField(default=datetime.now())
    updated = models.DateTimeField()
    expires = models.DateTimeField(blank=True, null=False)

    def __unicode__(self):
        if self.nickname:
            return u"%s (%s)" % (self.user.username, self.nickname)
        return self.user.username

    def display_name(self):
        return self.nickname or self.user.username

    def full_name(self):
        return u"%s %s" % (self.user.first_name, self.user.last_name)

    def get_absolute_url(self, request=None):
        if request is None:
            return reverse('profile_view', args=(self.user.username, ) )
        else:
            return urlparse.urljoin(
                getBaseURL(request), 
                reverse('profile_view', args=(self.user.username, ) )
                )

    def save(self):
        # if we're creating and the expiration date hasn't been set...
        if not(self.expires):

            # set the expiration to be now + 1 year
            today = datetime.now()
            self.expires = today.replace(today.year + 1)

        # set the updated timestamp
        self.updated = datetime.now()
            
        super(CommonerProfile, self).save()

    @property
    def active(self):
        """Return True if the profile is not expired."""

        return (datetime.now() < self.expires)

    @property
    def works(self):

        import commoner.works

        return commoner.works.models.Work.objects.filter(
            registration__owner__exact = self.user.id)

    @property
    def registrations(self):
        return self.user.registrations

    @property
    def badge_img_url(self):

        return "%s%s" % (settings.BADGE_BASE_URL, self.user.username)
    
