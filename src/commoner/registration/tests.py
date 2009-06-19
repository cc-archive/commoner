from django.test import TestCase
from django.core import mail
from commoner.registration import models

class TestRegistration(TestCase):
    fixtures = ['test_users.json', ]

    def test_add_registration(self):
        """Add a registration, make sure the welcome email is sent."""

        registration = models.PartialRegistration.objects.create_registration(
            1, 'test@example.com', 'Last', 'First', True)

        # we got something back, right?
        self.assert_(registration)

        # make sure the welcome email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['test@example.com'])

    def test_add_supress_email(self):
        """Add a registration without sending a welcome email."""

        registration = models.PartialRegistration.objects.create_registration(
            1, 'test@example.com', 'Last', 'First', False)
        
        self.assert_(registration)
        self.assertEqual(len(mail.outbox), 0)
                
    def test_resend_welcome(self):
        """Test that we can re-send the welcome email."""

        # create a registration without sending the welcome message
        registration = models.PartialRegistration.objects.create_registration(
            1, 'test@example.com', 'Last', 'First', False)
        
        self.assert_(registration)
        self.assertEqual(len(mail.outbox), 0)

        # now send it later, on demand
        models.PartialRegistration.objects.send_welcome(registration)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['test@example.com'])

    def test_complete(self):
        """Test completing the registration by filling out the form."""

        # create a registration without sending the welcome message
        registration = models.PartialRegistration.objects.create_registration(
            1, 'test@example.com', 'Last', 'First', False)
        
        # make sure we can get the completion page
        response = self.client.get(registration.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        # post the form
        response = self.client.post(registration.get_absolute_url(),
                                    dict(username='test',
                                         password1='test',
                                         password2='test',
                                         agree_to_tos=True))
        self.assertRedirects(response, '/a/register/complete/')

        # make sure we can log in
        self.client.login(username='test', password='test')

    def test_already_completed(self):
        """A registration may only be used once."""

        # create and complete a registration
        registration = models.PartialRegistration.objects.create_registration(
            1, 'test@example.com', 'Last', 'First', False)
        
        # post the form
        response = self.client.post(registration.get_absolute_url(),
                                    dict(username='test',
                                         password1='test',
                                         password2='test',
                                         agree_to_tos=True))
        self.assertRedirects(response, '/a/register/complete/')

        # try to visit the form again
        response = self.client.get(registration.get_absolute_url())
        self.assertContains(response, 
                            "This registration code has already been used.")

        # try to post the form by force
        response = self.client.post(registration.get_absolute_url(),
                                    dict(username='test2',
                                         password1='test',
                                         password2='test',
                                         agree_to_tos=True))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,
                            "This registration code has already been used.")
        self.assertTemplateUsed(response, 
                                'registration/complete_registration.html')

    def test_restricted_username(self):
        """Attempting to complete a registration with a restricted
        username should raise an error."""

        # create a registration
        registration = models.PartialRegistration.objects.create_registration(
            1, 'test@example.com', 'Last', 'First', False)
        
        # post the form
        response = self.client.post(registration.get_absolute_url(),
                                    dict(username='admin',
                                         password1='test',
                                         password2='test',
                                         agree_to_tos=True))
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'username',
                             ['This username is already taken. Please choose another.'])

    def test_short_username(self):
        """Completing a registration with a single character username
        raises an exception."""

        # create a registration
        registration = models.PartialRegistration.objects.create_registration(
            1, 'test@example.com', 'Last', 'First', False)
        
        # post the form
        response = self.client.post(registration.get_absolute_url(),
                                    dict(username='a',
                                         password1='test',
                                         password2='test',
                                         agree_to_tos=True))
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'username',
                             ['Usernames must be at least two characters long.']
                             )

    def test_duplicate_username(self):
        """A registration can not be completed with a duplicate 
        username."""

        # create a registration
        registration = models.PartialRegistration.objects.create_registration(
            1, 'test@example.com', 'Last', 'First', False)
        
        # post the form
        response = self.client.post(registration.get_absolute_url(),
                                    dict(username='testing',
                                         password1='test',
                                         password2='test',
                                         agree_to_tos=True))
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'username',
                             ['This username is already taken. Please choose another.'])

    def test_invalid_username(self):
        """A username can only contain letters, numbers and underscores."""

        # create a registration
        registration = models.PartialRegistration.objects.create_registration(
            1, 'test@example.com', 'Last', 'First', False)
        
        # post the form with a valid username
        response = self.client.post(registration.get_absolute_url(),
                                    dict(username='test_foo_123',
                                         password1='test',
                                         password2='test',
                                         agree_to_tos=True))
        self.assertRedirects(response, '/a/register/complete/')

        # create a registration
        registration = models.PartialRegistration.objects.create_registration(
            1, 'test2@example.com', 'Last', 'First', False)
        
        # post the form with a valid username
        response = self.client.post(registration.get_absolute_url(),
                                    dict(username='test_%123',
                                         password1='test',
                                         password2='test',
                                         agree_to_tos=True))

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'username',
                             ['Usernames can only contain letters, numbers and underscores.'])
    
    def test_free_registration(self):
        """Creating a free profile"""
        
        # create a registration via the Register form
        response = self.client.post('/a/register/', 
                            dict(first_name='First',
                                 last_name='Last',
                                 email='test@example.com'))
        
        self.assertContains(response, "verification email has been sent to your inbox")
        
        # verify that an email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['test@example.com'])
        
        # post the form to complete the registration
        registration = list(models.PartialRegistration.objects.filter(
                                    email='test@example.com'))[-1]
        response = self.client.post(registration.get_absolute_url(),
                                    dict(username='test_free',
                                         password1='test',
                                         password2='test',
                                         agree_to_tos=True))
        
        self.assertRedirects(response, '/a/register/complete/')

        # make sure we can log in
        self.client.login(username='test_free', password='test')
        