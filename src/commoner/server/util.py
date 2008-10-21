"""Utility methods for integrating OpenID server support."""

import datetime

from django.conf import settings

from commoner import util
from commoner.util import getViewURL, getBaseURL

__all__ = ['authorizeOpenId', 'getOpenIdUser', 'openIdAuthorized',
           'getOpenIDStore', 
           'setRequest', 'getRequest']

def getOpenIdExpiration():
    """Return a datetime.datetime object which is the time at which 
    the OpenID authorization will expire."""

    return datetime.datetime.now() + \
        datetime.timedelta(settings.OPENID_ENABLE_DAYS)

def authorizeOpenId(request, user=None):
    """Authorize this session for OpenID; if user is None the user will 
    not be manipulated."""

    request.session['openid_expires'] = getOpenIdExpiration()
    if user is not None:
        request.session['openid_user'] = user

def openIdAuthorized(request):
    """Return True if this session is authorized for OpenId."""

    if request.session.get('openid_user', None) is None:
        return False

    if request.session.get('openid_expires', datetime.datetime.now()) > \
            datetime.datetime.now():
        return True

    return False

def getOpenIdUser(request):
    """Check OpenID authorization for this session; if it's valid,
    return the associated user.  Otherwise return None."""

    if openIdAuthorized(request):
        return request.session['openid_user']

    return None

def getOpenIDStore():
    """
    Return an OpenID store object fit for the currently-chosen
    database backend, if any.
    """
    return util.getOpenIDStore('/tmp/djopenid_s_store', 's_')

def setRequest(request, openid_request):
    """
    Store the openid request information in the session.
    """
    if openid_request:
        request.session['openid_request'] = openid_request
    else:
        request.session['openid_request'] = None

def getRequest(request):
    """
    Get an openid request from the session, if any.
    """
    return request.session.get('openid_request')
