import urlparse

from django.db import models
from django.db.models import permalink
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from commoner.util import getBaseURL

class CommonerProfile(models.Model):
    
    user = models.ForeignKey(User, unique=True)

    nickname = models.CharField(max_length=255, blank=True)
    photo = models.ImageField(upload_to='p', blank=True, null=True)
    homepage = models.URLField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)

    story = models.TextField(blank=True)

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
                

