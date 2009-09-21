import os.path
import urlparse

from datetime import datetime, date

from django.db import models
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

class LogEntryManager(models.Manager):

    def record(self, message_id, message, obj=None, send_email=False):

        object_id, content_type = None, None
        
        if obj is not None:
            object_id = obj.pk
            content_type = ContentType.objects.get_for_model(obj)
                                
        return self.create(message_id=message_id,
                           message=message,
                           object_id=object_id,
                           content_type=content_type,
                           send_email=send_email)

class LogEntry(models.Model):
    """ Generic log entry class """
    
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_type = models.ForeignKey(ContentType, related_name="log_entries",
                                     blank=True, null=True)
    content_object = generic.GenericForeignKey()

    message_id = models.CharField(_("Event id string"), max_length=255)
    message = models.TextField(_("Log entry message"))

    created = models.DateTimeField(auto_now_add=True)

    send_email = models.BooleanField(_("Send email to webmaster"))

    objects = LogEntryManager()

    class Meta:
        verbose_name_plural = u'Log Entries'
    
    def __unicode__(self):
        return "[%s] <%s> %s" % (self.message_id,
                                 self.created,
                                 self.message,)
    
    def save(self, force_insert=False, force_update=False):
        
        super(LogEntry, self).save()

        if self.send_email:

            from django.core.mail import send_mail

            subject = u'CC.net <%s> event logged' % self.message_id
            send_mail(subject, str(self),  settings.DEFAULT_FROM_EMAIL, 
                  [admin[1] for admin in settings.ADMINS])        


        
    
