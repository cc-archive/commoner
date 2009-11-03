from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
import urllib2
import urlparse

class AddCitationForm(forms.Form):

    url = forms.URLField(label=_("Source url"), verify_exists=False)
    # if these are specified we won't scrape
    # title = ...
    # license = ...

    def clean_url(self):
        """

        The following code body is pulled directly from
        django.forms.fields.URLField.clean()

        This code is being replicated so limit the number of HTTP connections
        made to the url being cited.  When a citation is made, the resolved
        address of the url the user provided will be stored, which is obtained
        from a urllib response object.  When the superclasses clean method is
        called, and verify_exists is executed, a request is made that holds the
        resolved url.  So by storing that information here, 1 less HTTP request
        is needed.

        """
        value = self.cleaned_data.get('url')
        
        # If no URL scheme given, assume http://
        if value and '://' not in value:
            value = u'http://%s' % value
        # If no URL path given, assume /
        if value and not urlparse.urlsplit(value)[2]:
            value += '/'
            
        headers = {
            "Accept": "text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5",
            "Accept-Language": "en-us,en;q=0.5",
            "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
            "Connection": "close",
            "User-Agent": settings.URL_VALIDATOR_USER_AGENT,
        }
        
        try:
            self.request = urllib2.Request(value, None, headers)
            self.response = urllib2.urlopen(self.request)
            
        except ValueError:
            raise forms.ValidationError(self.fields['url'].error_messages['invalid'])
        except: # urllib2.URLError, httplib.InvalidURL, etc.
            raise forms.ValidationError(self.fields['url'].error_messages['invalid_link'])

        return value
    
class AddReuserForm(forms.Form):

    url = forms.URLField()

class AddMetadataForm(forms.Form):

    key = forms.CharField(max_length=128)
    value = forms.CharField(max_length=128)
