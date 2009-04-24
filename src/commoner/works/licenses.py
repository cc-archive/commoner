from lxml import etree as ET
from babel.messages import pofile
from django.conf import settings
import itertools, simplejson

class LicenseCatalog:

    XPATHS = {
        'licenses' :
            "//licenseclass[@id='%s']/license",
        'jurisdictions' :
            "//license[@id='%s']/jurisdiction",
        'versions' :
            "//license[@id='%s']/jurisdiction[@id='%s']/version",        
    }
    
    catalogs = {}
    licenses = {}

    def _localize(self, lang):
        
        """
        Because we already have these strings translated in another
        catalog derived from the License Engine, we will not tag these
        strings for translation with Django's i18n utilities.
        """
        
        # allocate for this lang
        self.catalogs[lang] = {}
        self.catalogs[lang]['l'] = {}
        self.catalogs[lang]['j'] = {}
        
        # convert the hyphens to underscores and get the path
        lang_code = settings.I18N_CCORG_ROOT % lang.replace('-','_')

        # get the po catalog for this language
        catalog = pofile.read_po(open(lang_code))

        # flatten the dictionary and remove dup.s
        juris = list(set(itertools.chain(*self.licenses.itervalues())))

        # translate the licenses names
        for lname in self.licenses.keys():
            # if the license name has not be translated yet
            if lname not in self.catalogs[lang]:
                self.catalogs[lang]['l'][lname] = catalog['licenses.pretty_%s' % lname].string

        # go through all of the jurisdictions
        for j in juris:

                if j not in self.catalogs[lang]['j']:

                    # Unported uses a different msgid
                    msgid = "country.%s" % j
                    
                    if j == '-': msgid = "util.Unported"

                    if msgid not in catalog:
                        self.catalogs[lang]['j'][j] = j
                    else:
                        self.catalogs[lang]['j'][j] = catalog[msgid].string
    
    def __init__(self, lang):
        
        # only do this once
        if len(self.licenses) == 0:

            t = ET.parse(settings.LICENSES_XML)

            # create a dict of what is returned from the xpath's
            self.licenses = dict(
                [ (l.get('id'), dict([
                    (j.get('id'), 
                        [v.get('id') 
                         for v in t.xpath( self.XPATHS['versions'] % (
                             l.get('id'),j.get('id') ) )])
                    for j in t.xpath( self.XPATHS['jurisdictions'] % 
                        l.get('id') )]))
                for l in t.xpath( self.XPATHS['licenses'] % 'standard' ) ])
            
        # if the language is not cached
        if lang not in self.catalogs:
            # translate for this lang
            self._localize(lang)

    def licenses_json(self, lang):
        
        # abbreviations for readability
        cl = self.catalogs[lang]['l']
        cj = self.catalogs[lang]['j']
        li = self.licenses     
        
        # form a 'json-like' dictionary to dump
        values = dict(
            [(l,{'name':cl.get(l,l),'jurisdictions': dict([
                (j, {'name':cj.get(j,j), 'versions': dict([
                    (v, v)
                    for v in li[l][j] ]) })
                for j in li[l] ]) })
             for l in li ])
        
        # dump a json string and sort the keys
        return simplejson.dumps(values, sort_keys=True)
        

