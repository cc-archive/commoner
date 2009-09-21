import os.path
import urlparse

from datetime import datetime, date

from django.db import models
from django.db.models import permalink
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string

from commoner.util import getBaseURL, get_storage
from commoner.registration.signals import user_activated

class CommonerProfileManager(models.Manager):

    def send_email_changed(self, newaddr, oldaddr):
        """Send the changed email notification."""

        from django.core.mail import send_mail

        current_site = Site.objects.get_current()
        subject = render_to_string('profiles/email/email_changed_subject.txt',
                                   {'site':current_site}).strip()
        message = render_to_string('profiles/email/email_changed_content.txt',
                                   {'site':current_site,
                                    'newaddr':newaddr})

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, 
                  [newaddr, oldaddr])        
    
class CommonerProfile(models.Model):
    """A User [Commoner] Profile; models additional user information 
    and provides convenience methods for accessing User properties."""
    
    FREE = 'free'
    PREMIUM = 'premium'
    ORGANIZATION = 'organization'
    PROFILE_LEVELS = [
        (FREE, _('Free')),
        (PREMIUM, _('Premium')),
        (ORGANIZATION, _('Organization'))
    ]

    user = models.ForeignKey(User, unique=True)

    # Select the level for this user, defaulted to 'premium' so that old code still works
    # TODO: rework registration to explicitly set level, change default to 'free'
    level = models.CharField(_("Level of profile"), choices=PROFILE_LEVELS,
                    max_length=255, default=FREE)

    gratis = models.BooleanField(_("Gratis profile"), default=False)
    
    nickname = models.CharField(_("Your name"), max_length=255, blank=True)
    photo = models.ImageField(_("Photo"), storage=get_storage(), 
                              upload_to='p', blank=True, null=True)

    homepage = models.URLField(_("Homepage"), max_length=255, blank=True)
    location = models.CharField(_("Location"), max_length=255, blank=True)

    story = models.TextField(blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    expires = models.DateTimeField(blank=True, null=False)
    
    redirect_https = models.BooleanField(default=True)

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
            
        super(CommonerProfile, self).save()

    @property
    def active(self):
        """Return True if the profile is not expired. Ignore the time of the
        expiration date. """

        return (date.today() < self.expires.date()) or self.gratis
    
    @property
    def is_legacy(self):
        """ Return True if the user isn't forced to use HTTPS for OpenID. """
        
        return not self.redirect_https

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

    def send_reminder_email(self):
        """ Send a reminder email to a user notifying that their account will
        soon be expired. Method accepts a `profile` parameter, of whom the email
        will be sent to based on profile.user.email and the profile.expires date.
        """
        from django.core.mail import send_mail
        import random
        
        # determine days before or past expiration on profile
        days = abs((self.expires.date() - date.today()).days)

        template = random.choice(['profiles/email/reminder_content_A.txt',
                     'profiles/email/reminder_content_B.txt',])
        
        current_site = Site.objects.get_current()
        subject = render_to_string('profiles/email/reminder_subject.txt',
                                   {'site':current_site,
                                    'active':self.active}).strip()
        message = render_to_string(template,
                                   {'site':current_site,
                                    'active':self.active, 'days':days})   
        
        return send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [self.email])
    
    def renew(self, expires_on=None):
        """ Update the profile by extending the expires date
        If the `expires_on` paramaeter is specifed, the expires date will be
        set to that datetime. """
        
        if expires_on is not None:
            self.expires = expires_on
        else:
            today = datetime.now()

            if self.active:
                self.expires = self.expires.replace(self.expires.year + 1)
            else:
                self.expires = today.replace(today.year + 1)
            
        return True

    def upgrade(self):
        """ Set the level to PREMIUM and set the expires date to +1 yr """

        self.level = self.PREMIUM
        self.expires = datetime.now().replace(datetime.now().year + 1)

        return True

    @property
    def is_organization(self):
        """ Return True if the profiles is an organization """
        
        return self.level == self.ORGANIZATION
 
    @property
    def premium(self):
        """ Returns True if the user was EVER ONCE a premium user.  Used for
        OpenID access control and also as a deterministic factor for the
        renewal/upgrade behavior. """

        return self.level == self.PREMIUM
    
    @property
    def free(self):
        """ Return True if this is a free account, meaning that the user has
        was a free registration or that their premium membership has expired.
        This property should be used in controlling the add works, citations, etc.
        """
        
        return self.level == self.FREE


# Callback function for commoner.registrations.signals.user_activated
def create_profile(sender, user, **kwargs):
    
    """ Creates a profile when a registration object is activated. """

    from commoner.registration.models import RegistrationProfile 
    
    reg = RegistrationProfile.objects.get(user=user)
    
    if reg.premium:
        level = CommonerProfile.PREMIUM
    else:
        level = CommonerProfile.FREE
        
    profile = CommonerProfile(user=user, level=level)
    profile.save()
    
    return profile
    
user_activated.connect(create_profile)
