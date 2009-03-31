from django.db import models
from django.contrib.auth.models import User, Group
from django.contrib.sessions.models import Session
from commoner.profiles.models import CommonerProfile

from django.template.defaultfilters import timesince
from django.utils.translation import gettext_lazy as _
from datetime import datetime

class Alert(models.Model):
    
    """ 
    Class Alert is essentially a wrapper of auth.Message
    These messages are displayed only once and to every user
    of the site 
    """
    
    author = models.ForeignKey(User)
    message = models.CharField(_('message'), max_length=200)
    date_created = models.DateTimeField(_('date created'))
        
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

class MessageManager(models.Manager):
    def get_query_set(self):
        return super(MessageManager, self).get_query_set().filter(
            enabled=True, 
            start_date__lte=datetime.now(),
            end_date__gte=datetime.now()
        )

class Message(models.Model):
    
    """
    Message
    """
    
    title = models.CharField(_('title'), max_length=100)
    content = models.TextField(_('message content'))
    start_date = models.DateTimeField(_('start date'), default=datetime.now)
    end_date = models.DateTimeField(_('end date'), blank=True, null=True)
    ack_req = models.BooleanField(_('acknowledgment required?'), default=False)
    enabled = models.BooleanField(_('enabled?'), default=False)
    
    objects = models.Manager()
    active = MessageManager()
    
    def __unicode__(self):
        return self.title
        
class Log(models.Model):
    user = models.ForeignKey(User)
    message = models.ForeignKey(Message)
    acked = models.BooleanField()