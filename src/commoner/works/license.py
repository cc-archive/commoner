from django import forms
from django.conf import settings
from lxml import etree as ET
from babel.messages import pofile

class LicenseSelectField(forms.MultiWidget):
    """
    A widget that allows a user to select a license using
    3 individual drop-downs; license name, jurisidiction, and version
    """
    __instance = None
    
    catalogs = {}

    licenses = {}
    
    def localize(self, lang):
        
        if lang not in self.catalogs.keys():
            
            self.catalogs[lang] = {}

            # get the po catalog for this language
            catalog = pofile.read_po(open(settings.I18N_CCORG_ROOT % lang))
            
            # we are going to translate any strings found in self.licenses
            for lname in self.licenses:

                if lname not in self.catalogs[lang]:
                    self.catalogs[lang][lname] = catalog['licenses.pretty_%s' % lname].string
                    
                for juris in self.licenses[lname]:
                    
                    if juris not in self.catalogs[lang]:
                        
                        if juris == '-':
                            msgid = "util.Unported"
                        else:
                            msgid = "country.%s" % juris

                        if msgid not in catalog:
                            self.catalogs[lang][juris] = ''
                        else:
                            self.catalogs[lang][juris] = catalog[msgid].string



    def __init__(self, lang=settings.LANGUAGE_CODE, name=None, juri=None, version=None):
        
        # TODO employ singleton pattern
        
        self.lang = lang

        t = ET.parse(settings.LICENSES_XML)

        lq = "//licenseclass[@id='standard']/license"
        jq = "//license[@id='%s']/jurisdiction"
        vq = "//license[@id='%s']/jurisdiction[@id='%s']/version"
        
        """
        Generates a dictionary mapping to what can be found in the XML
        """
        self.licenses = dict(
            [ (l.get('id'), dict([
                (j.get('id'), 
                    [v.get('id') 
                     for v in t.xpath( vq % (l.get('id'),j.get('id') ) )])
                for j in t.xpath( jq % l.get('id') )]))
            for l in t.xpath(lq)])
        
        self.localize(lang)
        



    def render(self, name=None, juri=None, version=None, attrs=None):
        
        self.html = """
            <select id='id_license_name'>
                <option value='by'>Attribution</option>
            </select>
        """

        return u'%s' % self.html
        
    
