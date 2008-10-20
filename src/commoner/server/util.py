"""Utility methods for integrating OpenID server support."""

import datetime

from django.conf import settings

from commoner import util
from commoner.util import getViewURL, getBaseURL

__all__ = ['getOpenIdExpiration', 'getOpenIDStore', 
           'setRequest', 'getRequest']

def getOpenIdExpiration():
    """Return a datetime.datetime object which is the time at which 
    the OpenID authorization will expire."""

    return datetime.datetime.now() + \
        datetime.timedelta(settings.OPENID_ENABLE_DAYS)

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
