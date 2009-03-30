import django.test 

from django.contrib import auth
from django.conf import settings
from commoner.profiles import models

class TestOpenID(django.test.TestCase):
    fixtures = ['test_https_users.json', ]
    
    def test_no_redirect_occurs(self):
        """ Verify that if the user is not legacy, 
        that a redirect is not allowed """
        
        settings.TESTING = False
        
        response = self.client.get('/normal/')
        # this should be forbidden
        self.assertEquals(response.status_code, 403)
    
    def test_redirect_occurs(self):
        """ The normal user is legacy, so allow the redirect """
        
        settings.TESTING = False
        
        response = self.client.get('/testing/')
        # we should get a moved permanently redirect
        self.assertEquals(response.status_code, 301)
        # since we can't actually open the https page, 
        # lets just verify that the 301 points there
        self.assertEquals(response['Location'], 'https://testserver/testing/')
        
    def test_argv_test_mode(self):
        """ Ensure the logic in settings.py properly detects the 'test' arg """
        self.assertTrue(settings.TESTING)    
        
    def test_middleware_toggle(self):
        """ Verify that the middleware is turned off during testing """

        settings.TESTING = True

        response = self.client.get('/normal/')
        # this should be forbidden
        self.assertEquals(response.status_code, 200)