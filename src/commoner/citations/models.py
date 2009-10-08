from django.db import models
from django.db.models import permalink
from django.contrib.admin.models import User
from django.i18n.util import gettext_lazy as _

class Citation(models.Model):
    
    # will we be support anonymous FTP locations? hope to god not
    cited_url = models.URLField(verify_exists=False) 
    resolved_url = models.URLField(verify_exists=False)
    
    cited_by = models.ForeignKey(User)
    cited_on = models.DateTimeField(auto_now_add=True)

    license_url = models.URLField(max_length=255, blank=True,
                                  help_text=_("The URL of the license this work is available under."))

    urlkey = models.CharField(max_length=5)
    
    def __unicode__(self):
        return self.urlkey

    @permalink
    def get_absolute_url(self):
        return "/c/%s" % self.urlkey
        
class MetaInfo(models.Model):
    """ """

    citation = models.ForeignKey(Citation, related_name="metainfo")
    
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

    # this field will be null for the metainfo that we scrape
    added_by = models.ForeignKey(User, blank=True, null=True)

    def __unicode__(self):
        return "%s - %s" % (self.citation, self.key,) 


class Reuser(models.Model):
     
    citation = models.ForeignKey(Citation, related_name="reusers")
     
    url = models.URLField(verify_exists=False)
    added_by = models.ForeignKey(User)
    added_on = models.DateTimeField(auto_now_add=True)
     
    def __unicode__(self):
        return "%s - %s" % (self.citation, self.url,)
     
    
