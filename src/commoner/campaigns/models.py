from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from datetime import datetime

class Campaign(models.Model):
    
    # need to do unique=True for the year
    user = models.ForeignKey(User, related_name='campaign', unique=True)
    
    pitch = models.TextField(_("why one should give"), blank=True)
    goal = models.DecimalField(_("fundraising goal"), max_digits=8, 
                                decimal_places=2)
    
    created = models.DateTimeField(default=datetime.now())
    updated = models.DateTimeField()
    
    expires = models.DateTimeField(_("end date for campaign"))
    
    def __unicode__(self):
        return "%s - $%s" % self.user, self.goal
    
    def save(self):
        """ Ensure dates are added/updated """
        
        # set the campaign expiration to the end of the current year
        # gives them a deadline for their fundraising
        if not self.expires:
            self.expires = datetime(datetime.now().year, 12, 31)
        
        self.updated = datetime.now()
        
        super(Campaign, self).save()
        
    @property
    def progress(self):
        """ Sum of the donations divided by the goal and rounded to the nearest
        percent """
        
        # donations not yet implemented so return zero
        return "0"