from django import forms
from commoner.content.models import Content

class ContentForm(forms.ModelForm):

    class Meta:
        model = Content
        exclude = ('user', )

class ContentDeleteForm(forms.Form):

    confirm_delete = forms.BooleanField(initial=False,
                                        label="Are you certain you want to remove this registration?")
    pass
