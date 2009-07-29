from django.test import TestCase
from django.core import mail
from commoner.registration import models

class TestRegistration(TestCase):
    fixtures = ['test_users.json', ]

    def test_create_registration(self):
        """
        positive case for registration form submission
        """

        response = self.client.get('/a/register/')
        self.assertEquals(response.code, 200)

        response = self.client.post('/a/register/', dict(
            username='test',
            email='test@example.com',
            first_name='First',
            last_name='Last',
            password1='password',
            password2='password',
            agree_to_tos=True))

        self.assertRedirects(response, '/a/register/check-inbox/')

      
            
         
        
        
