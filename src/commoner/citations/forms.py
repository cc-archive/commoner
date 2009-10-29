from django import forms

class AddReuserForm(forms.Form):

    url = forms.URLField()

class AddMetadataForm(forms.Form):

    key = forms.CharField(max_length=128)
    value = forms.CharField(max_length=128)
