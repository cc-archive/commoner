from django import forms
from django.utils.translation import ugettext_lazy as _

from commoner.works import models

class SimpleRegistrationForm(forms.Form):


    url = forms.URLField(label=_(u"Work URL"))
    title = forms.CharField(max_length=255)
    license_url = forms.URLField(label=_(u"License"),
                             help_text=_(u"The URL of the license your work is available under."))

    claim_all = forms.BooleanField(label=_(u"Register all works beginning with this URL?"),
                                   help_text=_(u"Use this option to register large groups of works that you have created. Note this is only appropriate if you own <strong>everything</strong> starting with this URL."),
                                   required=False)

    def __init__(self, user, instance={}, **kwargs):
        self._user = user
        self._instance = instance

        if self._instance and 'data' not in kwargs:
            # we have an instance, but no new data POSTed
            kwargs['data'] = dict(
                url = self._instance.url,
                title = self._instance.title,
                license_url = self._instance.license_url,
                claim_all = self._instance.has_leading_glob())

        super(SimpleRegistrationForm, self).__init__(**kwargs)

    def save(self):
        """If the registration/work exists, update the existing instance;
        otherwise add a new registration with a work."""

        if self._instance:

            # clear the leading glob if it already exists
            if self._instance.has_leading_glob():
                self._instance.constraints.all().delete()

            # update the existing instance
            self._instance.url = self.cleaned_data['url']
            self._instance.title = self.cleaned_data['title']
            self._instance.license_url = self.cleaned_data['license_url']

            self._instance.save()

            # add the leading glob if needed
            if self.cleaned_data.get('claim_all', False):
                models.Constraint.objects.add_leading_glob(self._instance)

            self._instance.save()

            return self._instance

        else:
            # create a new instance
            registration = models.Registration(owner=self._user)
            registration.save()

            work = models.Work(url=self.cleaned_data['url'],
                               title=self.cleaned_data['title'],
                               license_url=self.cleaned_data['license_url'])

            work.registration = registration        
            work.save()

            if self.cleaned_data.get('claim_all', False):
                # add the constraint
                models.Constraint.objects.add_leading_glob(work)

            return work
            
class FeedRegistrationForm(forms.Form):
    
    url = forms.URLField(label=_(u"Feed URL"))
    license_url = forms.URLField(label=_(u"License"),
                             help_text=_(u"The URL of the license your work is available under."))
                             
    consume_works = forms.BooleanField(label=_(u"Register the works listed in this feed."))
    monitor_updates = forms.BooleanField(label=_(u"Check this field regular and register new items."))

    def __init__(self, user, **kwargs):
        self._user = user
        super(FeedRegistrationForm, self).__init__(**kwargs)
    
    def clean_url(self):
        
        return self.cleaned_data['url']
    
    def save(self):
        
        registration = models.Registration(owner=self._user)
        registration.save()
        
        print "url = %s" % self.cleaned_data['url']
        
        feed = models.Feed(url=self.cleaned_data['url'],
                           license_url=self.cleaned_data['license_url'],
                           consume_works=self.cleaned_data['consume_works'],
                           monitor_updates=self.cleaned_data['monitor_updates'],
                           registration=registration)
        feed.save()
        
        