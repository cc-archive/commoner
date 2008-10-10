from django import forms
from django.core.files.storage import default_storage
from django.utils.translation import ugettext_lazy as _

from commoner.profiles.models import CommonerProfile

class CommonerProfileForm(forms.ModelForm):

    remove_photo = forms.BooleanField(label=_("Remove photo?"),
                                      required=False)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(CommonerProfileForm, self).__init__(*args, **kwargs)

    def clean_photo(self):
        """Rename the photo to match the profile username."""

        photo = self.cleaned_data.get('photo', False)
        if photo:
            photo.name = u'%s.%s' % (self.user.username,
                                     photo.name.split('.')[-1])

            if self.instance.photo:
                # remove the old photo
                default_storage.delete(self.instance.photo.path)

        return self.cleaned_data['photo']

    def save(self, *args, **kwargs):

        # see if we should remove the photo
        if self.instance and self.cleaned_data.get('remove_photo', False):
            self.instance.photo.delete()

        return super(CommonerProfileForm, self).save(*args, **kwargs)

    class Meta:
        model = CommonerProfile
        exclude = ('user','created','expires','updated')
