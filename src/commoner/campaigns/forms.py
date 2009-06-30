import re

from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from models import Campaign

class CampaignForm(forms.ModelForm):
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(CampaignForm, self).__init__(*args, **kwargs)
        
    class Meta:
        model = Campaign
        fields = ('pitch', 'goal')