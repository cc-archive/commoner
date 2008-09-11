from django import template
from django.template.defaultfilters import stringfilter

import cc.license

register = template.Library()

@register.filter
@stringfilter
def license_button(license_url):
    """Return the license button URL for a given license."""

    base_url = license_url.rsplit('/',1)[0]
    return "%s/80x15.png" % base_url.replace(
        'http://creativecommons.org/licenses/',
        'http://i.creativecommons.org/l/')


@register.filter
@stringfilter
def license_code(license_url):
    """Return the short license code for the license."""

    return "" 

    try:
        return cc.license.by_uri(license_url).code.upper()
    except cc.license.CCLicenseError, e:
        return ""

