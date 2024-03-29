
from django.test.testcases import TestCase
from commoner.server import views
from commoner import util
import util as server_util

from django.http import HttpRequest, QueryDict
from django.contrib.sessions.backends.cache import SessionStore
from django.contrib.auth.models import User

from openid.server.server import CheckIDRequest
from openid.message import Message
from openid.yadis.constants import YADIS_CONTENT_TYPE
from openid.yadis.services import applyFilter

def dummyRequest():
    request = HttpRequest()
    request.POST = QueryDict('', mutable=True)
    request.GET = QueryDict('', mutable=True)
    request.user = User.objects.get(username='normal')
    request.session = SessionStore("test")
    request.META['HTTP_HOST'] = 'example.invalid'
    request.META['SERVER_PROTOCOL'] = 'HTTP'
    return request

class TestSecurity(TestCase):
    fixtures = ['test_users.json', ]

    def testProcessTrustResultDirect(self):
        """Accessing process trust result directly shouldn't work."""
        
        response = self.client.get('/o/trust/')
        self.assertEqual(response.status_code, 403)

class TestProcessTrustResult(TestCase):
    fixtures = ['test_users.json', ]

    def setUp(self):
        self.request = dummyRequest()

        id_url = util.getViewURL(self.request, 'profile_view', args=('normal',))

        # Set up the OpenID request we're responding to.
        op_endpoint = 'http://127.0.0.1:8080/endpoint'
        message = Message.fromPostArgs({
            'openid.mode': 'checkid_setup',
            'openid.identity': id_url,
            'openid.return_to': 'http://127.0.0.1/%s' % (self.id(),),
            })
        self.openid_request = CheckIDRequest.fromMessage(message, op_endpoint)

        server_util.authorizeOpenId(self.request, User.objects.get(
                username='normal'))
        views.setRequest(self.request, self.openid_request)


    def test_allow(self):
        self.request.method = 'POST'
        self.request.POST['allow'] = 'Yes'

        response = views.trust_decision(self.request)

        self.failUnlessEqual(response.status_code, 302)
        finalURL = response['location']
        self.failUnless('openid.mode=id_res' in finalURL, finalURL)
        self.failUnless('openid.identity=' in finalURL, finalURL)

    def test_cancel(self):        
        self.request.method = 'POST'
        self.request.POST['cancel'] = 'Yes'

        response = views.trust_decision(self.request)

        self.failUnlessEqual(response.status_code, 302)
        finalURL = response['location']
        self.failUnless('openid.mode=cancel' in finalURL, finalURL)
        self.failIf('openid.identity=' in finalURL, finalURL)
        self.failIf('openid.sreg.postcode=12345' in finalURL, finalURL)


class TestShowDecidePage(TestCase):
    fixtures = ['test_users.json', ]
    def test_unreachableRealm(self):
        self.request = dummyRequest()

        id_url = util.getViewURL(self.request, 'profile_view', args=('testing',))
        # id_url = util.getViewURL(self.request, views.idPage)

        # Set up the OpenID request we're responding to.
        op_endpoint = 'http://127.0.0.1:8080/endpoint'
        message = Message.fromPostArgs({
            'openid.mode': 'checkid_setup',
            'openid.identity': id_url,
            'openid.return_to': 'http://unreachable.invalid/%s' % (self.id(),),
            'openid.sreg.required': 'postcode',
            })
        self.openid_request = CheckIDRequest.fromMessage(message, op_endpoint)

        views.setRequest(self.request, self.openid_request)

        response = views.show_trust_request(self.request)
        self.failUnless('trust_root_valid is Unreachable' in response.content,
                        response)



class TestGenericXRDS(TestCase):
    fixtures = ['test_users.json', ]
    def test_genericRender(self):
        """Render an XRDS document with a single type URI and a single endpoint URL
        Parse it to see that it matches."""
        request = dummyRequest()

        type_uris = ['A_TYPE']
        endpoint_url = 'A_URL'
        response = util.renderXRDS(request, type_uris, [endpoint_url])

        requested_url = 'http://requested.invalid/'
        (endpoint,) = applyFilter(requested_url, response.content)

        self.failUnlessEqual(YADIS_CONTENT_TYPE, response['Content-Type'])
        self.failUnlessEqual(type_uris, endpoint.type_uris)
        self.failUnlessEqual(endpoint_url, endpoint.uri)
