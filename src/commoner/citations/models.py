from django.db import models
from django.contrib.admin.models import User
from django.contrib.sites.models import Site
from django.utils.translation import gettext_lazy as _

from commoner.util import base62string, attributionHTML, attributionText

from commoner.citations.rdf.store import RdfaStore
from commoner.citations.rdf import helper

URLKEY_LEN = 5

class CitationManager(models.Manager):
    
    def create(self, **kwargs):

        if 'urlkey' not in kwargs.keys():
            kwargs['urlkey'] = base62string(URLKEY_LEN)

        return super(CitationManager, self).create(**kwargs)

    def get_or_cite(self, **kwargs):
        """ checking those fingerprints, NYI """
        
        try:
            citation = self.get(**kwargs)
                    
        except self.model.DoesNotExist:

            kwargs['urlkey'] = base62string(URLKEY_LEN)
            while self.filter(urlkey = kwargs['urlkey']):
                kwargs['urlkey'] = base62string(URLKEY_LEN)

            citation = self.create(**kwargs)
            
        return citation, 'urlkey' in kwargs
    
class Citation(models.Model):

    title = models.CharField(max_length=256, blank=True)
    
    cited_url = models.URLField(verify_exists=False) 
    resolved_url = models.URLField(verify_exists=False)
    
    cited_by = models.ForeignKey(User)
    cited_on = models.DateTimeField(auto_now_add=True)

    license_url = models.URLField(max_length=255, blank=True,
                                  help_text=_("The URL of the license this work is available under."))

    urlkey = models.CharField(max_length=URLKEY_LEN, unique=True)
    
    objects = CitationManager()
    
    def __unicode__(self):
        return self.urlkey

    @models.permalink
    def get_absolute_url(self):
        return ('citation_view', (), {'cid':str(self.urlkey),})

    def canonical_url(self, request=None, scheme='https'):
        if request is None:
            hostname = "%s://%s" % (scheme, Site.objects.get_current().domain,)
        else:
            hostname = request.META.get('HTTP-HOST')

        return hostname + self.get_absolute_url()

    def triples(self):
        return RdfaStore('webcitations').get_graph(self.canonical_url())

    @property
    def license(self):
        """ shorthand and mneumonic accessor for license_url """
        return self.license_url
    @property
    def cclicensed(self):
        """ Technically a license url could come in that is not a cc url """
        return "http://creativecommons.org" in self.license_url
    
    """
    Retrieve licensing information for the cited work.
    If the citation does not have a license url store in the model, then
    to avoid any RDF store interaction, just return some plain attribution text.
    """
    def _licensed(attrib_func):
        def conditioned_func(self):
            if not self.cclicensed:
                return ''
            return attrib_func(self)
        return conditioned_func
    
    @property
    @_licensed
    def attributionName(self):
        return helper.get_attribution_name(self.triples(), self.resolved_url)
    @property
    @_licensed
    def attributionURL(self):
        return helper.get_attribution_url(self.triples(), self.resolved_url)
    @property
    @_licensed
    def attribution_html(self):
        return attributionHTML(self.resolved_url, self.license_url,
                               self.attributionURL, self.attributionName)
    @property
    @_licensed
    def attribution_text(self):
        return attributionText(self.resolved_url, self.license_url, self.title,
                               self.attributionURL, self.attributionName)

class MetaDataManager(models.Manager):

    def store_triple(self, predicate, obj):
        """ store_triple accepts the predicate and object from an RDF triple
        and stores the values in the metadata table for quicker lookups.
        Ideally the RDFa that is scraped from a cited work should be
        displayed to the user in a human readable format.  This requires
        the use of rdfs:label properties, which is an expensive query.
        """
        pass
        
    
class MetaData(models.Model):
    """ """

    citation = models.ForeignKey(Citation, related_name="metadata")
    
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
     
    
