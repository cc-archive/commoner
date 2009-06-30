from decimal import Decimal
from datetime import datetime

import django.test 
from django.contrib import auth

from commoner.campaigns import models

class TestCampaigns(django.test.TestCase):
    fixtures = ['test_users.json', ]

    def setUp(self):
        self.client.login(username='normal', password='testing')

    def test_add_campaign(self):
        """ Start a campaign for our normal user """
        
        response = self.client.get('/p/campaign/')
        self.assertEquals(response.status_code, 200)
        
        response = self.client.post('/p/campaign/', dict(
                        pitch='Test campaign add',goal='1000'))
        # make sure we were redirected
        self.assertEqual(response.status_code, 302)
        
        campaign = list(models.Campaign.objects.filter(
                user__username = 'normal').all())[-1]
        
        # ensure data matches what was submitted
        self.assertEqual(campaign.pitch, 'Test campaign add')
        self.assertEqual(campaign.goal, Decimal('1000'))
        # verify dates were stamped
        self.assertTrue(isinstance(campaign.created, datetime))
        self.assertTrue(isinstance(campaign.updated, datetime))
        # expiration should be end of current year
        self.assertEquals(campaign.expires, datetime(datetime.now().year,12,31))
        
    def test_edit_campaigns(self):
        """ Edit a campaign's pitch and goal """
        
        response = self.client.post('/p/campaign/', dict(
                        pitch='Test campaign add',goal='1000'))
        self.assertEqual(response.status_code, 302)
        
        # get the campaign we just created
        campaign = list(models.Campaign.objects.filter(
                user__username = 'normal').all())[-1]
                
        response = self.client.get('/p/campaign/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'Edit Campaign')
        self.assertContains(response, 'Test campaign add')
        
        response = self.client.post('/p/campaign/', dict(
                        pitch='Test campaign edit',goal='10000'))
        self.assertEquals(response.status_code, 302)
                        
        edit_campaign = models.Campaign.objects.get(id=campaign.id)
        self.assertEqual(edit_campaign.pitch, 'Test campaign edit')
        self.assertEqual(edit_campaign.goal, Decimal('10000'))