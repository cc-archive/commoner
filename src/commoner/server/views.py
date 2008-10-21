import cgi
import urllib
import urlparse
from datetime import datetime

from commoner import util
from commoner.util import getViewURL, getBaseURL

from django import http
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.contrib import auth

from django.views.generic.simple import direct_to_template
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from openid.server.server import Server, ProtocolError, CheckIDRequest, \
     EncodingError
from openid.server.trustroot import verifyReturnTo
from openid.yadis.discover import DiscoveryFailure
from openid.consumer.discover import OPENID_IDP_2_0_TYPE
from openid.consumer.discover import OPENID_2_0_TYPE
from openid.extensions import sreg
from openid.fetchers import HTTPFetchingError

from util import *
import forms
from django.contrib.sites.models import Site
from models import TrustedRelyingParty, TrustedMetadata

def getServer(request):
    """
    Get a Server object to perform OpenID authentication.
    """
    return Server(getOpenIDStore(), getViewURL(request, endpoint))

def idpXrds(request):
    """
    Respond to requests for the IDP's XRDS document, which is used in
    IDP-driven identifier selection.
    """
    return util.renderXRDS(
        request, [OPENID_2_0_TYPE], [getViewURL(request, endpoint)])

def login(request):
    """Handle OpenID enable/login requests."""

    s = getServer(request)
    next = request.REQUEST.get('next', request.META.get('HTTP-REFERER', '/'))

    if request.method == 'POST':

        # process the form
        form = forms.OpenIdLoginForm(request.POST.get('id', None),
                                     data=request.POST)

        try:
            if form.is_valid():
                authorizeOpenId(request, 
                                auth.models.User.objects.get(
                        username__exact=form.cleaned_data['username'])
                                )

                return http.HttpResponseRedirect(next)
        except AssertionError:
            # treason uncloaked!
            openid_request = s.decodeRequest(
                dict(cgi.parse_qsl(request.REQUEST.get('next'))))

            error_response = ProtocolError(
                openid_request.message,
                "This server cannot verify the URL %r" %
                (openid_request.identity,))

            return displayResponse(request, error_response)
            

    else:
        id_url = request.GET.get('id', '')
        initial = dict(secret = forms.make_secret(id_url))
        if id_url:
            initial.update(dict(username = urlparse.urlsplit(id_url)[2][1:-1]))

        form = forms.OpenIdLoginForm(id_url,
                                     initial=initial)

    return render_to_response("server/login.html",
                              dict(form=form,
                                   site=Site.objects.get_current(),
                                   next=next),
                              context_instance=RequestContext(request))

def endpoint(request):
    """
    Respond to low-level OpenID protocol messages.
    """
    s = getServer(request)

    query = util.normalDict(request.GET or request.POST)

    # Convert the django request to one the OpenID library understand
    try:
        openid_request = s.decodeRequest(query)
    except ProtocolError, why:
        # invalid request
        return direct_to_template(
            request,
            'server/endpoint.html',
            {'error': str(why)})

    # make sure we received a request
    if openid_request is None:
        return direct_to_template(
            request,
            'server/endpoint.html',
            {})

    # We got a request; if the mode is checkid_*, we will handle it by
    # getting feedback from the user or by checking the session.
    if openid_request.mode in ["checkid_immediate", "checkid_setup"]:
        return handleCheckIDRequest(request, openid_request)
    else:
        # We got some other kind of OpenID request, so we let the
        # server handle this.
        openid_response = s.handleRequest(openid_request)
        return displayResponse(request, openid_response)

def handleCheckIDRequest(request, openid_request):
    """
    Handle checkid_* requests.  Get input from the user to find out
    whether she trusts the RP involved.  Possibly, get input about
    what Simple Registration information, if any, to send in the
    response.
    """

    # store the incoming request object
    setRequest(request, openid_request)

    # check if we're operating in immediate mode
    if openid_request.immediate:

        # immediate mode -- see if the user is logged in
        if openIdAuthorized(request):
            
            # user has logged into OpenID and auth hasn't expired yet
            # see if they've already said they want to trust this root
            try:
                trusted_site = getOpenIdUser(request).\
                    trusted_parties.get(root = 
                                        openid_request.trust_root)

                # we trust this site
                return createOpenIdResponse(request, True, False,
                                            [m.field_name for m in
                                            trusted_site.metadata.all()]
                                            )


            except TrustedRelyingParty.DoesNotExist, e:
                pass

        # immediate mode -- we can't say yes, fall back to cancel
        return createOpenIdResponse(request, allowed=False)

    # Not immediate mode 
    # ------------------
    # Check if the user is authenticated and has enabled OpenID
    if openIdAuthorized(request):

        # and it's the user we were asked to verify
        if getOpenIdUser(request).get_profile().get_absolute_url(
            request=request) == openid_request.identity:

            # see if we've previously trusted this root
            try:
                trusted_site = getOpenIdUser(request).\
                    trusted_parties.get(root = 
                                        openid_request.trust_root)

                # we trust this site
                return createOpenIdResponse(request, True, False,
                                            [m.field_name for m in
                                             trusted_site.metadata.all()]
                                            )

            
            except TrustedRelyingParty.DoesNotExist, e:
                pass

            return show_trust_request(request)
        
    # need to authenticate the user (or auth expired)
    return login_redirect(request, openid_request)

def sreg_fields(sreg_request, user, allowed_fields = None):

    sreg_data = {}

    if allowed_fields is None:
        allowed_fields = sreg_request.allRequestedFields()

    if sreg_request.allRequestedFields():
        if 'email' in allowed_fields:
            sreg_data['email'] = user.email
        if 'nickname' in allowed_fields:
            sreg_data['nickname'] = user.get_profile().display_name()
        if 'fullname' in allowed_fields:
            sreg_data['fullname'] = user.get_profile().full_name()

    return sreg_data
        
def show_trust_request(request):

    openid_request = getRequest(request)
    if openid_request is None:
        return http.HttpResponseForbidden('No OpenID request.')

    # ZZZ make sure the logged in user matches the request IDP URL
    trust_root = openid_request.trust_root
    return_to = openid_request.return_to

    # see if the server requested SREG
    sreg_request = sreg.SRegRequest.fromOpenIDRequest(openid_request)

    try:
        # Stringify because template's ifequal can only compare to strings.
        trust_root_valid = verifyReturnTo(trust_root, return_to) \
                           and "Valid" or "Invalid"
    except DiscoveryFailure, err:
        trust_root_valid = "DISCOVERY_FAILED"
    except HTTPFetchingError, err:
        trust_root_valid = "Unreachable"

    return direct_to_template(
        request,
        'server/trust.html',
        {'trust_root': trust_root,
         'trust_handler_url':getViewURL(request, trust_decision),
         'trust_root_valid': trust_root_valid,
         'sreg_request':sreg_request,
         'sreg_data' : sreg_fields(sreg_request, getOpenIdUser(request))
         })

def updateStoredTrust(request):
    """Store the trust_root and selected SREG fields."""

    user = getOpenIdUser(request)
    openid_request = getRequest(request)

    # add the trust relationship for the trust_root
    trusted_rp = TrustedRelyingParty(user=user, root=openid_request.trust_root)
    trusted_rp.save()

    # add the selected SREG fields
    if request.REQUEST.getlist('allow_sreg'):
        allowed_fields = request.REQUEST.getlist('allow_sreg')
        for field in allowed_fields:
            trusted_rp.metadata.add(TrustedMetadata(field_name=field))

def trust_decision(request):
    """
    Process the result of making a trust decision.
    """

    if request.method == 'POST':
        # process the result of the trust decision
        allowed = 'allow' in request.POST
        remember = (request.POST.get('remember', 'off') == 'on')

        if allowed and remember:
            updateStoredTrust(request)

        return createOpenIdResponse(request, allowed, remember,
                                    request.POST.getlist('allow_sreg'))

    return http.HttpResponseForbidden("Denied.")

def createOpenIdResponse(request, allowed=False, remember=False,
                         allowed_fields=[]):
    """Craft a response (allowed or not) and return it. Before rendering
    we clear the OpenID request from the session."""

    # Get the request from the session so we can construct the
    # appropriate response.
    openid_request = getRequest(request)

    # The identifier that this server can vouch for
    response_identity = getOpenIdUser(request).get_profile().\
        get_absolute_url(request=request)

    # Generate a response with the appropriate answer.
    openid_response = openid_request.answer(allowed,
                                            identity=response_identity)

    # populate extensions as necessary
    sreg_request = sreg.SRegRequest.fromOpenIDRequest(openid_request)

    if allowed:
        # renew the authorization
        authorizeOpenId(request)

        if sreg_request.allRequestedFields():
            # add SREG fields if requested
            # see if we're allowing anything
            sreg_data = sreg_fields(sreg_request, getOpenIdUser(request),
                                    allowed_fields)

            sreg_resp = sreg.SRegResponse.extractResponse(sreg_request, 
                                                          sreg_data)
            openid_response.addExtension(sreg_resp)
            
    # clear the openId request
    setRequest(request, None)

    return displayResponse(request, openid_response)

def displayResponse(request, openid_response):
    """
    Display an OpenID response.  Errors will be displayed directly to
    the user; successful responses and other protocol-level messages
    will be sent using the proper mechanism (i.e., direct response,
    redirection, etc.).
    """
    s = getServer(request)

    # Encode the response into something that is renderable.
    try:
        webresponse = s.encodeResponse(openid_response)
    except EncodingError, why:
        # If it couldn't be encoded, display an error.
        text = why.response.encodeToKVForm()
        return direct_to_template(
            request,
            'server/endpoint.html',
            {'error': cgi.escape(text)})

    # Construct the appropriate django framework response.
    r = http.HttpResponse(webresponse.body)
    r.status_code = webresponse.code

    for header, value in webresponse.headers.iteritems():
        r[header] = value

    return r

@login_required
def settings(request):

    return render_to_response('profiles/openid_settings.html', 
                              dict(site=Site.objects.get_current()),
                              context_instance=RequestContext(request))

@login_required
def delete_trusted_party(request, id):

    # get the trusted party
    trusted_party = get_object_or_404(TrustedRelyingParty, id=id)
    if trusted_party.user != request.user:
        # prohibited
        return http.HttpResponseForbidden("Forbidden.")

    if request.method == 'POST':

        # make sure it was submitted with the confirm button
        if request.POST.get('confirm', False):

            # remove the object
            trusted_party.delete()
            
            # redirect to the settings page
            return http.HttpResponseRedirect(reverse('openid_settings'))

    return render_to_response('server/delete_trusted_party.html',
                              dict(trusted_party=trusted_party),
                              context_instance=RequestContext(request))
def login_redirect(request, openid_request=None):

    if openid_request is None:
        openid_request = getRequest(request)

    # determine what the next URL would be after logging in
    query = util.normalDict(request.GET or request.POST)
    query_string = urllib.urlencode(
        [(k, v) 
         for k, v in query.iteritems()
         if k[:7] == 'openid.']
        )
    next_url = "%s?%s" % (
        reverse('commoner.server.views.endpoint'), query_string)

    # redirect to the login page
    return http.HttpResponseRedirect("%s?%s" % (
            reverse('openid_login'),
            urllib.urlencode([('id', openid_request.identity,),
                              ('next', next_url),])
            ))

def state(request):
    """Return the state of OpenID authorization for Seatbelt support."""

    result = ["""<?xml version="1.0" encoding="UTF-8" ?>""",
              """<personaConfig version="1.0" serverIdentifier="creativecommons.net">"""]

    if openIdAuthorized(request):

        # someone is logged in; add their information
        user = getOpenIdUser(request).get_profile()
        result.append(
            """<persona displayName="%s">%s</persona>""" % (
                user.display_name(), user.get_absolute_url(request=request))
            )

    result.append("""</personaConfig>""")

    return http.HttpResponse("\n".join(result),
                             mimetype='text/xml')
