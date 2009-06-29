import django.test 

from django.contrib import auth

import models

class TestCampaigns(django.test.TestCase):
    fixtures = ['test_users.json', ]

    def setUp(self):
        self.client.login(username='normal', password='testing')

    def test_create_campaign(self):
        """ Start a campaign for our normal user """
        
        response = self.client.get('/p/campaign/')
        self.assertEquals(response.status_code, 200)