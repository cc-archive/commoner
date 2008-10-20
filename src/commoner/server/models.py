from django.db import models

from django.contrib.auth.models import User

class TrustedRelyingParty(models.Model):

    user = models.ForeignKey(User, related_name='trusted_parties')
    root = models.CharField(max_length=255)

    def __unicode__(self):
        return self.root

