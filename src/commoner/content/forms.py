from django import forms
from commoner.content.models import Content

class ContentForm(forms.ModelForm):

    class Meta:
        model = Content
        exclude = ('user', )
