from django.test import TestCase
from django.conf import settings
from django.core import mail
from commoner.registration import models

class TestContact(TestCase):

    def test_use_contact(self):
        """Submit the contact form, make sure the mail is sent."""

        response = self.client.get('/h/contact/')
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/h/contact/',
                                    dict(sender='user@example.com',
                                         subject='Test Message',
                                         message='Hello, world.'))

        self.assertRedirects(response, '/h/contact/thanks/')

        # make sure the contact email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [m[1] for m in settings.MANAGERS])
