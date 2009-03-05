from django import forms
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.utils.translation import ugettext_lazy as _

from commoner.profiles.models import CommonerProfile

class ChangeEmailForm(forms.Form):
    
    new_email = forms.EmailField(label="New e-mail address")
    new_email_verify = forms.EmailField(label="Verify new e-mail address")
    
    def clean_new_email(self):    
        # make sure this user does not exist
        new_email = self.cleaned_data.get('new_email')
        try:
            user = User.objects.get(email__iexact=new_email)
        except User.DoesNotExist:
            return self.cleaned_data['new_email']

        raise forms.ValidationError(_(u'This email is already in use. Please choose another.'))
    
    def clean_new_email_verify(self):
        """ check to make sure email addresses match and they are unique """
        
        new_email = self.cleaned_data.get('new_email')
        verified_input = self.cleaned_data.get('new_email_verify')
        
        if new_email != verified_input:
            raise forms.ValidationError(_(u'Your email addresses did not match, try again.'))
        
        return self.cleaned_data['new_email_verify']

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