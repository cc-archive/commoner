from django import forms
from licenses import LicenseCatalog

class SelectInput(forms.Select):

    selectors = []
    
    def __init__(self, selectors={}, *args, **kwargs):

        self.selectors = selectors
        
        super(SelectInput, self).__init__(*args, **kwargs)

    def render(self, name, value):

        html = "<select name='%s'>\n" % name

        for c in self.choices:
                        
            html += "<option class='%s' value='%s'>%s</option>" % \
                    (self.selectors.get(c,""), c[0], c[1])

        html += "</select>"

        return html

class LicenseField(forms.MultiValueField):

    def __init__(self, lang, *args, **kwargs):

        # fetch the licenses data
        lc = LicenseCatalog(lang)

        i18n = lc.catalogs[lang]
        
        f1 = forms.Select(choices=sorted([
            (l, i18n.get(l, l)) for l in lc.licenses.keys()]))
        f2 = forms.Select(choices=sorted([
            (j, i18n.get(j, j)) for j in lc.licenses['by']], key=lambda a:a[1]))
        f3 = forms.Select(choices=[('1.0','1.0'),('2.0', '2.0')])
            
        flds = (f1,f2,f3,)
                
        super(LicenseField, self).__init__(flds, *args, **kwargs)
        
    def compress(self, data):
        return data

    def render(self):
        """ render the html for the chain select """
        html = self.fields[0].render('id_licenses_name', 'by') + \
               self.fields[1].render('id_licenses_jurisdiction', '-') + \
               self.fields[2].render('id_licenses_version', '')

        return html


