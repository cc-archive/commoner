import os.path
import urlparse

from datetime import datetime

from django.db import models
from django.db.models import permalink
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.conf import settings

from commoner.util import getBaseURL

class CommonerProfile(models.Model):
    
    user = models.ForeignKey(User, unique=True)

    nickname = models.CharField("Screen name", max_length=255, blank=True)
    photo = models.ImageField(upload_to='p', blank=True, null=True)

    homepage = models.URLField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)

    story = models.TextField(blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    expires = models.DateTimeField(blank=True, null=False)

    def __unicode__(self):
        if self.nickname:
            return u"%s (%s)" % (self.user.username, self.nickname)
        return self.user.username

    def display_name(self):
        return self.nickname or self.user.username

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
        if not(self.created) and not(self.expires):

            # set the expiration to be now + 1 year
            today = datetime.now()
            self.expires = today.replace(today.year + 1)
            
        super(CommonerProfile, self).save()

    @property
    def active(self):
        """Return True if the profile is not expired."""

        return (datetime.now() < self.expires)

    @property
    def content(self):
        return self.user.content

    @property
    def badge_img_url(self):

        return "%s%s" % (settings.BADGE_BASE_URL, self.user.username)
    
