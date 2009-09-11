import django.test 

from django.contrib import auth
from commoner.profiles import models

class TestEdit(django.test.TestCase):
    fixtures = ['test_users.json', ]
    
    def setUp(self):
        
        self.client.login(username='normal', password='testing')
        
    
    def test_edit_profile(self):
        """ Edit a user's profile information """

        profile_data = {
            'nickname' : u'Larry Lessig',
            'homepage' : u'http://lessig.org/', # uses check_exists, can't be bogus
            'location' : u'Mars',
            'story'    : u'Erutluc Eerf'
        }
        
        # post new profile information
        response = self.client.post('/p/edit/', profile_data)
        
        profile = models.CommonerProfile.objects.get(user__username='normal')
        
        self.assertEqual(profile.nickname, profile_data['nickname'])
        self.assertEqual(profile.homepage, profile_data['homepage'])
        self.assertEqual(profile.location, profile_data['location'])
        self.assertEqual(profile.story,    profile_data['story'])
        

    def test_edit_email(self):
        """ Edit a user's email address """
        
        response = self.client.post('/p/email/', 
                        dict(new_email='foo@bar.com', 
                             new_email_verify='foo@bar.com'))
        
        
        profile = models.CommonerProfile.objects.get(user__username='normal')
        
        self.assertEqual(profile.email, 'foo@bar.com')
        
        