import os.path
import urlparse

from datetime import datetime

from django.db import models
from django.db.models import permalink
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string

from commoner.util import getBaseURL, get_storage

class CommonerProfileManager(models.Manager):

    def send_email_changed(self, newaddr, oldaddr):
        """Send the changed email notification."""

        from django.core.mail import send_mail

        current_site = Site.objects.get_current()
        subject = render_to_string('profiles/email/subject.txt',
                                   {'site':current_site}).strip()
        message = render_to_string('profiles/email/content.txt',
                                   {'site':current_site,
                                    'newaddr':newaddr})

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, 
                  [newaddr, oldaddr])
    
class CommonerProfile(models.Model):
    """A User [Commoner] Profile; models additional user information 
    and provides convenience methods for accessing User properties."""

    PROFILE_LEVELS = [
        ('free', _('free')),
        ('premium', _('premium')),
        ('organization', _('organization'))
    ]

    user = models.ForeignKey(User, unique=True)

    # Select the level for this user, defaulted to 'premium' so that old code still works
    # TODO: rework registration to explicitly set level, change default to 'free'
    level = models.CharField(_("Level of profile"), choices=PROFILE_LEVELS,
                    max_length=255, default='free')
    
    nickname = models.CharField(_("Screen name"), max_length=255, blank=True)
    photo = models.ImageField(_("Photo"), storage=get_storage(), 
                              upload_to='p', blank=True, null=True)

    homepage = models.URLField(_("Homepage"), max_length=255, blank=True)
    location = models.CharField(_("Location"), max_length=255, blank=True)

    story = models.TextField(blank=True)

    created = models.DateTimeField(default=datetime.now())
    updated = models.DateTimeField()
    expires = models.DateTimeField(blank=True, null=False)
        
    objects = CommonerProfileManager()
    
        
    def __unicode__(self):        
        if self.nickname:
            return u"%s (%s)" % (self.user.username, self.nickname)
        return self.user.username

    def display_name(self):
        return self.nickname or self.user.username

    def full_name(self):
        """Return the full name associated with this profile; this is 
        a convenience that concatenates the first and last name from the
        User model."""
        
        if self.is_organization and self.nickname:
            return self.nickname
        
        return u"%s %s" % (self.user.first_name, self.user.last_name)

    @property
    def email(self):
        return self.user.email

    def get_absolute_url(self, request=None):
        """Return the absolute URL for the CommonerProfile; if a
        request is specified, returns a fully qualified URL."""
        
        if request is None:
            return reverse('profile_view', args=(self.user.username, ) )
        else:
            return urlparse.urljoin(
                getBaseURL(request), 
                reverse('profile_view', args=(self.user.username, ) )
                )

    def save(self):
        # if we're creating and the expiration date hasn't been set...
        if not(self.expires):

            # set the expiration to be now + 1 year
            today = datetime.now()
            self.expires = today.replace(today.year + 1)

        # set the updated timestamp
        self.updated = datetime.now()
            
        super(CommonerProfile, self).save()

    @property
    def active(self):
        """Return True if the profile is not expired."""

        return (datetime.now() < self.expires)

    @property
    def works(self):
        """Return a list of Work objects registered with this 
        profile's User."""

        import commoner.works

        return commoner.works.models.Work.objects.filter(
            registration__owner__exact = self.user.id)

    @property
    def registrations(self):
        """Return a list of Registration objects registered for this
        profile's User."""

        return self.user.registrations

    @property
    def badge_img_url(self):
        """Return the fully qualified URL for the member badge."""

        return "%s%s/" % (settings.BADGE_BASE_URL, self.user.username)

    @property
    def thin_badge_img_url(self):
        """Return the fully qualified URL for the slim member badge."""

        return "%s%s/80x15/" % (settings.BADGE_BASE_URL, self.user.username)
        
    @property
    def free(self):
        """ Return True if this is a free account """
        
        # TODO : should inactive users be considered FREE ?
        return self.level == 'free'
