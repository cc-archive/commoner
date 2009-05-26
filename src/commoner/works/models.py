from urlparse import urlparse
from datetime import datetime

from django.db import models

from django.db import models
from django.db.models import permalink
from django.core.urlresolvers import reverse

from commoner.util import getBaseURL

from commoner.profiles.models import CommonerProfile
from django.contrib.auth.models import User

class Registration(models.Model):

    owner = models.ForeignKey(User, 
                              related_name='registrations',
                              blank=True, null=True)
    created = models.DateTimeField(default = datetime.now())
    updated = models.DateTimeField()

    def __unicode__(self):
        return u"%s - %s" % (self.owner, self.created)

    def save(self):
        # set the updated timestamp
        self.updated = datetime.now()

        super(Registration, self).save()
    
class Work(models.Model):

    registration = models.ForeignKey(Registration,
                                     related_name='works')

    url = models.URLField(max_length=255, blank=False,
                          verify_exists=False,
                          verbose_name="Work URL")

    title = models.CharField(max_length=255, blank=True)
    license_url = models.URLField(max_length=255, blank=True,
                            help_text="The URL of the license your work is available under.")

    registered = models.DateTimeField(default=datetime.now())
    updated = models.DateTimeField()

    same_as = models.ForeignKey("self", blank=True, null=True)

    class Meta:
        ordering = ['-registered']
    def get_absolute_url(self):
        return reverse('view_work', args=(self.id,))

    def __unicode__(self):
        return self.title or self.url

    def save(self, *args, **kwargs):
        # set the updated timestamp
        self.updated = datetime.now()

        super(Work, self).save(*args, **kwargs)

    @property
    def owner_user(self):
        return self.registration.owner

    @property
    def owner(self):
        return self.registration.owner.get_profile()

    @property
    def license(self):
        """Return the license name for the specified URL; 
        fall back to the URL."""

        return self.license_url

    ##
    ## Constraint convenience properties
    ## 

    @property
    def constrained(self):
        return self.constraints.count() > 0

    def has_leading_glob(self):
        """Return True if the given Work has a simple, "prefix" glob.

        First, create a work:

        >>> r = Registration()
        >>> r.save()
        >>> w = Work(registration=r,title='Test Work', url='http://example.com/work',
        ...          license='http://creativecommons.org/licenses/by/3.0/')
        >>> w.save()

        With no constraints, we by definition are not a simple glob:

        >>> w.has_leading_glob()
        False

        Now add a leading glob constraint:

        >>> Constraint.objects.add_leading_glob(w)

        We can check for this:
        >>> w.has_leading_glob()
        True

        Constraints are additive; adding a second one (even a no-op)
        causes this to return False:
        >>> c2 = Constraint(constraint='schemes', mode='include', var='http')
        >>> w.constraints.add(c2)
        >>> w.has_leading_glob()
        False

        """

        # we must have three constraints to qualify
        if self.constraints.count() != 3:
            return False

        try:
            url = urlparse(self.url)

            # look for each constraint
            self.constraints.get(mode='include',
                                 constraint='hosts',
                                 var=url[1])
            self.constraints.get(mode='include',
                                 constraint='pathstartswith',
                                 var=url[2])
            self.constraints.get(mode='include',
                                 constraint='schemes',
                                 var=url[0])

            return True
        except:
            return False
                

class ConstraintManager(models.Manager):

    def add_leading_glob(self, work):
        """Create the constraints necessary to claim all works that
        begin with the given URL."""

        url = urlparse(work.url)
        work.constraints.add(
            Constraint(mode='include',
                       constraint='hosts',
                       var=url[1]))
        work.constraints.add(
            Constraint(mode='include',
                       constraint='pathstartswith',
                       var=url[2]))
        work.constraints.add(
            Constraint(mode='include',
                       constraint='schemes',
                       var=url[0]))


class Constraint(models.Model):

    REGEXES = dict(
        schemes = r'^var\:\/\/',
        hosts = r'\:\/\/(([^\/\?\#]*)\@)?([^\:\/\?\#\@]+\.)?var(\:([0-9]+))?\/',
        ports = r'\:\/\/(([^\/\?\#]*)\@)?([^\:\/\?\#\@]+\.)*[^\:\/\?\#\@]+\:var\/',
        exactpaths = r'\:\/\/(([^\/\?\#]*)\@)?([^\:\/\?\#\@]*)(\:([0-9]+))?var($|\?|\#)',
        pathcontains = r'\:\/\/(([^\/\?\#]*)\@)?([^\:\/\?\#\@]*)(\:([0-9]+))?\/[^\?\#]*var[^\?\#]*[\?\#]?',
        pathstartswith = r'\:\/\/(([^\/\?\#]*)\@)?([^\:\/\?\#\@]*)(\:([0-9]+))?var',
        pathendswith = r'\:\/\/(([^\/\?\#]*)\@)?([^\:\/\?\#\@]*)(\:([0-9]+))?\/[^\?\#]*var($|\?|\#)',
        resources = r'^var$',
        )

    ESCAPE_CHARS = """. \ ? * + { } ( ) [ ] ! " # % & ' , - / : ; = > @ [ ] _ ` ~""".strip()

    CONSTRAINTS = (
        ('schemes',        'schemes'),
        ('hosts',          'hosts'),
        ('ports',          'ports'),
        ('exactpaths',     'exactpaths'),
        ('pathcontains',   'pathcontains'),
        ('pathstartswith', 'pathstartswith'),
        ('pathendswith',   'pathendswith'),
        ('resources',      'resources'),
        )

    MODES = (
        ('include', 'include'),
        ('exclude', 'exclude'),
        )

    work = models.ForeignKey(Work, related_name='constraints',
                             null=True, blank=True)
    
    constraint = models.CharField(max_length=20, choices=CONSTRAINTS)
    mode = models.CharField(max_length=20, choices=MODES)

    var = models.CharField(max_length=255)

    objects = ConstraintManager()

    @property
    def regex_var(self):
        """Return the processed version of self.var as described by 
        http://www.w3.org/TR/2008/WD-powder-formal-20080815/#whitespace"""
    
        result = self.var.strip()
        result = result.replace(' ', '|')
        
        var = u""
        for c in result:
            if c in self.ESCAPE_CHARS:
                var += u"\%s" % c
            else:
                var += c

        return u"(%s)" % var

    @property
    def predicate(self):
        return u"%s%s" % (self.mode, self.constraint)

    @property
    def regex(self):
        """Return a regex for the given constraint as described by 
        http://www.w3.org/TR/2008/WD-powder-formal-20080815/#iriSets"""

        return self.REGEXES[self.constraint].replace('var', self.regex_var)

class Feed(models.Model):

    """ This model wasn't being used in the previous version, I imagine it was
    stubbed here for future development """
    
    registration = models.ForeignKey(Registration,
                                     related_name='feeds')
                                     
    url = models.URLField(max_length=255, blank=False, verify_exists=False)
    license_url = models.URLField(max_length=255, blank=True)
    cron_enabled = models.BooleanField(default=True, 
                help_text="Run a cron job to periodically consume the works in this feed.")
        
    consumed = models.DateTimeField()

    def __unicode__(self):
        return "%s - %s" % (self.registration.owner, self.url)

    @property
    def owner_user(self):
        return self.registration.owner
    
    def save(self):
        # set the updated timestamp
        self.consumed = datetime.now()

        super(Feed, self).save()