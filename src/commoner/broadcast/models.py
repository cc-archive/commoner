from django.db import models
from django.contrib.auth.models import User, Group
from django.contrib.sessions.models import Session
from commoner.profiles.models import CommonerProfile

from django.template.defaultfilters import timesince
from django.utils.translation import gettext_lazy as _
from datetime import datetime

class SimpleAlert(models.Model):
    
    """ 
    A SimpleAlert is an alert that can be sent out across
    all users of a given site through to use of auth.Message.
    These messages are displayed only once and to every user
    of the site 
    """
    
    author = models.ForeignKey(User)
    message = models.CharField(_('message'), max_length=200)
    date_created = models.DateTimeField(_('date created'))
    
    class Meta:
        verbose_name = "Simple Alert"
    
    def __unicode__(self):
        return self.message
    
    def save(self, force_insert=False, force_update=False):
        # get all of the current Commoners
        self.dispatch(msg="%s -- Posted %s ago" % \
            ( self.message, timesince(self.date_created) ))
        super(Alert, self).save(force_insert, force_update)
    
    def dispatch(self, msg):
        users = CommonerProfile.objects.filter(expires__gte=datetime.now())
        for u in users:
            u.user.message_set.create(message=msg)

class RobustAlertManager(models.Manager):
    def get_query_set(self):
        return super(RobustAlertManager, self).get_query_set().filter(
            enabled=True, 
            start_date__lte=datetime.now(),
            end_date__gte=datetime.now()
        )

class RobustAlert(models.Model):
    
    """
    Robust Alert is what the name implies, 
    inspiration: djangosnippets.org/snippets/1310/
    TODO - assignment of alerts to individual views
    TODO - assignment to groups of users
    """
    
    author = models.ForeignKey(User)
    title = models.CharField(_('title'), max_length=100)
    content = models.TextField(_('message content'))
    target = models.ManyToManyField(Group, blank=True)
    view_limit = models.IntegerField(_('view limit'), 
        help_text=_('The maximum number of time the user must see this alert.'),
        default=1, null=0)
    per_session = models.BooleanField(_('once per session?'), default=True)
    start_date = models.DateTimeField(_('start date'))
    end_date = models.DateTimeField(_('end date'))
    enabled = models.BooleanField(_('enabled?'), default=False)
    
    objects = models.Manager()
    active = RobustAlertManager()
    
    def __unicode__(self):
        return self.title
    
    class Meta:
        verbose_name = "Robust Alert"    
        
class AlertLog(models.Model):
    user = models.ForeignKey(User)
    alert = models.ForeignKey(RobustAlert)
    session = models.CharField(max_length=40)