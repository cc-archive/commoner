from django.forms import ModelForm
from commoner.profiles.models import CommonerProfile

class CommonerProfileForm(ModelForm):

    class Meta:
        model = CommonerProfile
        exclude = ('user',)
