import django.test
from django.conf import settings

class TestMessagesDisplay(django.test.TestCase):
    
    fixtures = ['test_messages.json', 'test_users.json']
    
    def setUp(self):
        self.client.login(username='john', password='john')
    
    def testShowEnabled(self):
        """ Test to ensure an enabled message does show."""
        response = self.client.get('/john')
        
        self.assertContains(response, "***Enabled Message***")
        response = self.client.get('/john')
        self.assertNotContains(response, "***Enabled Message***")        
    
    def testDontShowExpired(self):
        """ Test to ensure an expired message does not show."""
        response = self.client.get('/john')
        
        self.assertNotContains(response, "***Expired Message***")
        
    def testAcknowledge(self):
        """ Test to ensure an acked message does not show."""
        response = self.client.get('/john')

        self.assertContains(response, "***Requires Ack***")
        response = self.client.get('/a/ack/2')
        self.assertRedirects(response, "/john")
        response = self.client.get('/john')
        self.assertNotContains(response, "***Requires Ack***")
        
    def testDontShowDisabled(self):
        """ Test to ensure a disabled message does not show."""
        response = self.client.get('/john')

        self.assertNotContains(response, "***Disabled Message***")
