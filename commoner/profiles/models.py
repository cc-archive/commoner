from django.db import models
from django.db.models import permalink
from django.contrib.auth.models import User

class CommonerProfile(models.Model):
    
    user = models.ForeignKey(User, unique=True)

    homepage = models.CharField(max_length=200, blank=True)

    def __unicode__(self):
        return self.user

    @permalink
    def get_absolute_url(self):
        return ('profiles.views.profile_detail', (str(self.user),))

