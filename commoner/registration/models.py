import sha
import random

from django.db import models
from django.db.models import permalink

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

