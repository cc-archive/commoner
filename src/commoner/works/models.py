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

class Feed(Registration):

    url = models.URLField(max_length=255, blank=False, verify_exists=False)
    license = models.URLField(max_length=255, blank=True)    



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

    def get_absolute_url(self):
        return reverse('view_work', args=(self.id,))

    def __unicode__(self):
        return self.title or self.url

    def save(self):
        # set the updated timestamp
        self.updated = datetime.now()

        super(Work, self).save()

    @property
    def owner(self):
        return self.registration.owner

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

    def is_simple_glob(self):
        """Return True if the given Work has a simple, "prefix" glob.

        First, create a work:

        >>> r = Registration()
        >>> r.save()
        >>> w = Work(registration=r,title='Test Work', url='http://example.com/work',
        ...          license='http://creativecommons.org/licenses/by/3.0/')
        >>> w.save()

        With no constraints, we by definition are not a simple glob:

        >>> w.is_simple_glob()
        False

        Now add a constraint:

        >>> c = Constraint.objects.create_simple_glob(w.url)
        >>> w.constraints.add(c)

        We can check for this:
        >>> w.is_simple_glob()
        True

        Constraints are additive; adding a second one (even a no-op)
        causes this to return False:
        >>> c2 = Constraint(component='scheme', matching_rule='exact', mode='include', value='http')
        >>> w.constraints.add(c2)
        >>> w.is_simple_glob()
        False

        """

        # we must have one and only one constraint to qualify
        if self.constraints.count() != 1:
            return False

        # we have only one constraint; see if it matches
        constraint = self.constraints.all()[0]
        return (constraint.component == 'ipath') and \
            (constraint.matching_rule == 'startsWith') and \
            (constraint.mode == 'include') and \
            (constraint.value == self.url)
                

class ConstraintManager(models.Manager):

    def create_simple_glob(self, prefix):
        """Return a newly created, simple "glob" constraint."""

        constraint = Constraint(
            component = 'ipath',
            matching_rule = 'startsWith',
            mode ='include',
            value=prefix)
        constraint.save()

        return constraint

class Constraint(models.Model):
    
    COMPONENTS = (
        ('scheme', 'scheme'),
        ('ihost',  'ihost'),
        ('ipath',  'ipath'),
        ('port',   'port'),
        )
    MATCHING_RULES = (
        ('exact', 'exact'),
        ('endswith', 'endswith'),
        ('contains', 'contains'),
        ('startsWith', 'startsWith'), 
        ('endsWith', 'endsWith'),
        )
    MODES = (
        ('include', 'include'),
        ('exclude', 'exclude'),
        )

    work = models.ForeignKey(Work, related_name='constraints',
                             null=True, blank=True)
    
    component = models.CharField(max_length=20, choices=COMPONENTS)
    matching_rule = models.CharField(max_length=20, choices=MATCHING_RULES)
    mode = models.CharField(max_length=20, choices=MODES)

    value = models.CharField(max_length=255)

    objects = ConstraintManager()

    def match(self, input):
        """Run this constraint against the given input.  Return True
        if the input matches."""

        raise NotImplementedError()
