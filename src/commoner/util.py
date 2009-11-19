import os
from urlparse import urljoin

from django.db import connection
from django.template.context import RequestContext
from django.template import loader
from django import http
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse as reverseURL
from django.core.urlresolvers import NoReverseMatch
from django.views.generic.simple import direct_to_template
from django.core.files.storage import FileSystemStorage

from django.conf import settings

from openid.store.filestore import FileOpenIDStore
from openid.store import sqlstore
from openid.yadis.constants import YADIS_CONTENT_TYPE

def getOpenIDStore(filestore_path, table_prefix):
    """
    Returns an OpenID association store object based on the database
    engine chosen for this Django application.

    * If no database engine is chosen, a filesystem-based store will
      be used whose path is filestore_path.

    * If a database engine is chosen, a store object for that database
      type will be returned.

    * If the chosen engine is not supported by the OpenID library,
      raise ImproperlyConfigured.

    * If a database store is used, this will create the tables
      necessary to use it.  The table names will be prefixed with
      table_prefix.  DO NOT use the same table prefix for both an
      OpenID consumer and an OpenID server in the same database.

    The result of this function should be passed to the Consumer
    constructor as the store parameter.
    """
    if not settings.DATABASE_ENGINE:
        return FileOpenIDStore(filestore_path)

    # Possible side-effect: create a database connection if one isn't
    # already open.
    connection.cursor()

    # Create table names to specify for SQL-backed stores.
    tablenames = {
        'associations_table': table_prefix + 'openid_associations',
        'nonces_table': table_prefix + 'openid_nonces',
        }

    types = {
        'postgresql': sqlstore.PostgreSQLStore,
        'mysql': sqlstore.MySQLStore,
        'sqlite3': sqlstore.SQLiteStore,
        }

    try:
        s = types[settings.DATABASE_ENGINE](connection.connection,
                                            **tablenames)
    except KeyError:
        raise ImproperlyConfigured, \
              "Database engine %s not supported by OpenID library" % \
              (settings.DATABASE_ENGINE,)

    try:
        s.createTables()
    except (SystemExit, KeyboardInterrupt, MemoryError), e:
        raise
    except:
        # XXX This is not the Right Way to do this, but because the
        # underlying database implementation might differ in behavior
        # at this point, we can't reliably catch the right
        # exception(s) here.  Ideally, the SQL store in the OpenID
        # library would catch exceptions that it expects and fail
        # silently, but that could be bad, too.  More ideally, the SQL
        # store would not attempt to create tables it knows already
        # exists.
        pass

    return s

def getViewURL(req, view_name_or_obj, args=None, kwargs=None):
    relative_url = reverseURL(view_name_or_obj, args=args, kwargs=kwargs)
    full_path = req.META.get('SCRIPT_NAME', '') + relative_url
    return urljoin(getBaseURL(req), full_path)

def getBaseURL(req):
    """
    Given a Django web request object, returns the OpenID 'trust root'
    for that request; namely, the absolute URL to the site root which
    is serving the Django request.  The trust root will include the
    proper scheme and authority.  It will lack a port if the port is
    standard (80, 443).
    """
    name = req.META.get('HTTP_HOST', '')
    try:
        name = name[:name.index(':')]
    except:
        pass

    try:
        port = int(req.META['SERVER_PORT'])
    except:
        port = 80

    proto = req.META['SERVER_PROTOCOL']

    if 'HTTPS' in proto or req.is_secure():
        proto = 'https'
    else:
        proto = 'http'

    if port in [80, 443] or not port:
        port = ''
    else:
        port = ':%s' % (port,)

    url = "%s://%s%s/" % (proto, name, port)
    return url

def normalDict(request_data):
    """
    Converts a django request MultiValueDict (e.g., request.GET,
    request.POST) into a standard python dict whose values are the
    first value from each of the MultiValueDict's value lists.  This
    avoids the OpenID library's refusal to deal with dicts whose
    values are lists, because in OpenID, each key in the query arg set
    can have at most one value.
    """

    return dict((k, v) for k, v in request_data.iteritems())

def renderXRDS(request, type_uris, endpoint_urls):
    """Render an XRDS page with the specified type URIs and endpoint
    URLs in one service block, and return a response with the
    appropriate content-type.
    """
    response = direct_to_template(
        request, 'xrds.xml',
        {'type_uris':type_uris, 'endpoint_urls':endpoint_urls,})
    response['Content-Type'] = YADIS_CONTENT_TYPE
    return response

def get_storage():
    """Return the storage instance to use for user-uploaded content."""

    return FileSystemStorage(
        location = os.path.join(settings.MEDIA_ROOT, settings.USER_STORAGE),
        base_url = os.path.join(settings.MEDIA_URL, settings.USER_STORAGE))

    
def base_url_context(request):
    """Django Context Processor which adds the {{base_url}} to the
    context."""

    return dict(base_url=getBaseURL(request)[:-1])

def services_url_context(request):
    """Django Context Processor which adds a dict of service URLs to the 
    context."""

    try:
        lookup_work=getViewURL(request, "lookup_work")
    except NoReverseMatch, e:
        lookup_work = ""

    services = dict(lookup_work=lookup_work)

    return dict(services=services)


import string, random
BASE62 = string.letters + string.digits
def base62string(length):
    return ''.join([random.choice(BASE62) for i in range(0,length)])

class CCLicenseError(Exception):
    pass

""" taken from cc.license._lib.functions """
def ccuri2dict(uri):
    """Take a license uri and convert it into a dictionary of values.

    >>> sorted(ccuri2dict('http://creativecommons.org/licenses/by/3.0/deed.en').items())
    [('code', 'by'), ('jurisdiction', 'Unported'), ('version', '3.0')]
    >>> sorted(ccuri2dict('http://creativecommons.org/licenses/by/3.0/').items())
    [('code', 'by'), ('jurisdiction', 'Unported'), ('version', '3.0')]
    >>> sorted(ccuri2dict('http://creativecommons.org/licenses/by/3.0/us/').items())
    [('code', 'by'), ('jurisdiction', 'us'), ('version', '3.0')]
    >>> sorted(ccuri2dict('http://creativecommons.org/licenses/by/3.0/us').items())
    ------------------------------------------------------------
    Traceback (most recent call last):
    ...
    CCLicenseError: Malformed Creative Commons URI: <http://creativecommons.org/licenses/by/3.0/us>
    >>> sorted(ccuri2dict('http://creativecommons.org/licenses/by/3.0').items())
    ------------------------------------------------------------
    Traceback (most recent call last):
    ...
    CCLicenseError: Malformed Creative Commons URI: <http://creativecommons.org/licenses/by/3.0>
    >>> sorted(ccuri2dict('http://creativecommons.org/publicdomain/zero/1.0/').items())
    [('code', 'CC0'), ('jurisdiction', None), ('version', '1.0')]
    >>> sorted(ccuri2dict('http://creativecommons.org/publicdomain/zero/').items())
    ------------------------------------------------------------
    Traceback (most recent call last):
    ...
    CCLicenseError: Malformed Creative Commons URI: <http://creativecommons.org/publicdomain/zero/>
    """
    
    std_base = 'http://creativecommons.org/licenses/'
    cc0_base = 'http://creativecommons.org/publicdomain/zero/'

    if 'deed' in uri:
        uri = uri[:uri.rindex('deed')]

    if uri.startswith(std_base) and uri.endswith('/'):
        raw_info = uri[len(std_base):]
        raw_info = raw_info.rstrip('/')
        info_list = raw_info.split('/')
        
        if len(info_list) not in (2,3):
            raise CCLicenseError, "Malformed Creative Commons URI: <%s>" % uri
            
        retval = dict( code=info_list[0], jurisdiction='Unported' )
        if len(info_list) > 1:
            retval['version'] = info_list[1]
        if len(info_list) > 2:
            retval['jurisdiction'] = info_list[2]

        return retval
    
    elif uri.startswith(cc0_base) and uri.endswith('/'):

        retval = { 'code':'CC0', 'jurisdiction': None }
        retval['version'] = uri[len(cc0_base):].split('/')[0]
        if retval['version'] is '':
            raise CCLicenseError, "Malformed Creative Commons URI: <%s>" % uri
        return retval

    else:
        raise CCLicenseError, "Malformed Creative Commons URI: <%s>" % uri
        
        
def attributionHTML(subject, license_url, attribURL=None, attribName=None):

    try:
       cclicense = ccuri2dict(license_url)
    except ValueError, e:
       # Only valid CC licenses are supported
       return u''

    div = '<div xmlns:cc="http://creativecommons.org/ns#" about="%s">%%s</div>' % subject
    if attribURL:
        attrib = '<a rel="cc:attributionURL"%%shref="%s">%%s</a>' % attribURL
        if attribName:
            attrib = attrib % (' property="cc:attributionName" ', attribName,)
        else:
            attrib = attrib % (' ', attribURL,)
    elif attribName:
        attrib = '<span property="cc:attributionName">%s</span>' % attribName
    else:
        attrib = '<span>%s</span>' % subject
    attrib += ' / <a rel="license" href="%s">CC %s</a>' % (license_url,
                                                           cclicense['code'].upper(),)

    return unicode(div % attrib)     

def attributionText(subject, license_url, title=None, attribURL=None, attribName=None):
    try:
       cclicense = ccuri2dict(license_url)
    except ValueError, e:
       # Only valid CC licenses are supported
       return u''
    attrib = title or subject
    if attribName:
        attrib += " by %s" % attribName
    attrib += ", available under a CC %s license." % cclicense['code'].upper()
    return unicode(attrib)
