from django import template
from django.template.defaultfilters import stringfilter
import re

try:
    import cc.license
except ImportError, e:
    pass

register = template.Library()

@register.filter
@stringfilter
def license_button(license_url):
    """Return the license button URL for a given license."""
    # strip trailing slash
    base_url = license_url.rsplit('/',1)[0]
    
    base_urls = {
        'http://creativecommons.org/licenses':
            'http://i.creativecommons.org/l',
        'http://creativecommons.org/publicdomain/zero/1.0':
            'http://i.creativecommons.org/p',
    }
    
    pattern = re.compile('|'.join(map(re.escape, base_urls)))
    img_url = pattern.sub(lambda m: base_urls[m.group(0)], base_url)
    return "%s/80x15.png" % img_url


@register.filter
@stringfilter
def license_code(license_url):
    """Return the short license code for the license."""

    return "" 

    try:
        return cc.license.by_uri(license_url).code.upper()
    except cc.license.CCLicenseError, e:
        return ""

