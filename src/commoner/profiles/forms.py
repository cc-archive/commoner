from django.forms import ModelForm
from commoner.profiles.models import CommonerProfile

class CommonerProfileForm(ModelForm):

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(CommonerProfileForm, self).__init__(*args, **kwargs)

    def clean_photo(self):
        """Rename the photo to match the profile username."""

        photo = self.cleaned_data.get('photo', False)
        if photo:
            photo.name = u'%s.%s' % (self.user.username,
                                     photo.name.split('.')[-1])

        return self.cleaned_data['photo']

    class Meta:
        model = CommonerProfile
        exclude = ('user',)
