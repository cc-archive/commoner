from django.db import models
from django.db.models import permalink
from django.contrib.auth.models import User

class Content(models.Model):

    commoner = models.ForeignKey(User)

    title = models.CharField(max_length=255, blank=True)
    url = models.URLField(max_length=255, blank=False)

    def __unicode__(self):
        return self.title or self.url

    @permalink
    def get_absolute_url(self):
        return ('profiles.views.content_detail', (self.id,))

class CommonerProfile(models.Model):
    
    user = models.ForeignKey(User, unique=True)

    nickname = models.CharField(max_length=255, blank=True)
    homepage = models.URLField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)

    def __unicode__(self):
        if self.nickname:
            return u"%s (%s)" % (self.user.username, self.nickname)
        return self.user.username

    @permalink
    def get_absolute_url(self):
        return ('commoner.profiles.views.profile_view', (str(self.user),))

