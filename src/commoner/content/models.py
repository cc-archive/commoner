from django.db import models

from django.db import models
from django.db.models import permalink
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from commoner.util import getBaseURL

class Content(models.Model):

    commoner = models.ForeignKey(User, related_name='content')

    title = models.CharField(max_length=255, blank=True)
    url = models.URLField(max_length=255, blank=False)

    license = models.URLField(max_length=255, blank=True)

    def __unicode__(self):
        return self.title or self.url

