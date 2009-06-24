from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from datetime import datetime

class Campaign(models.Model):
    
    user = models.ForeignKey(User, related_name='campaign', unique=True)
    
    pitch = models.TextField(_("why one should give"), blank=True)
    goal = models.DecimalField(_("fundraising goal"), max_digits=8, 
                                decimal_places=2)
    
    created = models.DateTimeField(default=datetime.now())
    starts = models.DateTimeField(_("start date for campaign"))
    expires = models.DateTimeField(_("end date for campaign"))
    
    def __unicode__(self):
        return "%s - $%s" % self.user, self.goal
