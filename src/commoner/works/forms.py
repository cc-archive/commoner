from django import forms

from commoner.works import models

class SimpleRegistrationForm(forms.Form):


    url = forms.URLField(label="Work URL")
    title = forms.CharField(max_length=255)
    license_url = forms.URLField(label="License",
                             help_text="The URL of the license your work is available under.")

    def __init__(self, user, instance={}, **kwargs):
        self._user = user
        self._instance = instance

        if self._instance and 'data' not in kwargs:
            # we have an instance, but no new data POSTed
            kwargs['data'] = dict(
                url = self._instance.url,
                title = self._instance.title,
                license_url = self._instance.license_url)

        super(SimpleRegistrationForm, self).__init__(**kwargs)

    def save(self):
        """If the registration/work exists, update the existing instance;
        otherwise add a new registration with a work."""

        if self._instance:
            # update
            self._instance.url = self.cleaned_data['url']
            self._instance.title = self.cleaned_data['title']
            self._instance.license_url = self.cleaned_data['license_url']

            self._instance.save()

            return self._instance

        else:
            # create a new instance
            registration = models.Registration(owner=self._user)
            registration.save()

            work = models.Work(**self.cleaned_data)
            work.registration = registration
        
            work.save()

            return work
