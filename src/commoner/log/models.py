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
    
    def __unicode__(self):
        return "[%s] <%s> %s" % (self.message_id,
                                 self.created,
                                 self.message,)

    def __init__(self, message_id, message, obj=None,
                 *args, **kwargs):
        
        super(LogEntry, self).__init__(*args, **kwargs)

        if obj:
            self.object_id = obj.pk
            self.content_type = ContentType.objects.get_for_model(obj)
                                
        self.message_id = message_id
        self.message = message

    def save(self):
        
        super(LogEntry, self).save()

        if self.send_email:

            from django.core.mail import send_mail

            subject = u'CC.net <%s> event logged' % self.message_id
            send_mail(subject, str(self),  settings.DEFAULT_FROM_EMAIL, 
                  [admin[1] for admin in settings.ADMINS])        


        
    
