from django.forms.fields import ChoiceField, MultiValueField
from django.forms.widgets import Select, MultiWidget
from django import forms

from licenses import LicenseCatalog
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

import hashlib
import random

class LicenseSelectorWidget(MultiWidget):
    
    licenses = [
        ('by' , 'Attribution'),
        ('by-sa' , 'Attribution-ShareAlike'),
        ('by-nd' , 'Attribution-NoDerivs'),
        ('by-nc' , 'Attribution-NonCommercial'),
        ('by-nc-sa' , 'Attribution-NonCommercial-ShareAlike'),
        ('by-nd-nc' , 'Attribution-NoDerivs-NonCommercial'),
    ]
    
    def __init__(self, attrs=None):
        
        wdgts = (
            Select(attrs, choices=self.licenses), 
            Select(attrs),
            Select(attrs),
        )
        
        super(LicenseSelectorWidget, self).__init__(wdgts, attrs)
    
    
    def render(self, name, value, attrs=None):
        return mark_safe(super(LicenseSelectorWidget, self).render(name, value, attrs=attrs))    
            
            
    def decompress(self, value):
        return value or (None, None)
        
class LicenseSelectorField(MultiValueField):
    widget = LicenseSelectorWidget
    
    def __init__(self, lang, *args, **kwargs):
        #lc = LicenseCatalog(lang)
        flds = (ChoiceField(),ChoiceField(),ChoiceField())
        super(LicenseSelectorField, self).__init__(fields=flds, *args, **kwargs)
    
    def compress(self, data):
        return data