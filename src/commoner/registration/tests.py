"""
Unit tests for django-registration.

These tests assume that you've completed all the prerequisites for
getting django-registration running in the default setup, to wit:

1. You have ``registration`` in your ``INSTALLED_APPS`` setting.

2. You have created all of the templates mentioned in this
   application's documentation.

3. You have added the setting ``ACCOUNT_ACTIVATION_DAYS`` to your
   settings file.

4. You have URL patterns pointing to the registration and activation
   views, with the names ``registration_register`` and
   ``registration_activate``, respectively, and a URL pattern named
   'registration_complete'.

"""

import datetime
import sha

from django.conf import settings
from django.contrib.auth.models import User
from django.core import mail
from django.core import management
from django.core.urlresolvers import reverse
from django.test import TestCase

from commoner.registration import forms
from commoner.registration.models import RegistrationProfile
from commoner.registration import signals


class RegistrationTestCase(TestCase):
    """
    Base class for the test cases; this sets up two users -- one
    expired, one not -- which are used to exercise various parts 
    of the application.
    """
    def setUp(self):
        self.sample_user = RegistrationProfile.objects.create_inactive_user(username='alice',
                                                                            password='secret',
                                                                            email='alice@example.com')
        self.expired_user = RegistrationProfile.objects.create_inactive_user(username='bob',
                                                                             password='swordfish',
                                                                             email='bob@example.com')
        self.expired_user.date_joined -= datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS + 1)
        self.expired_user.save()


class RegistrationModelTests(RegistrationTestCase):
    """
    Tests for the model-oriented functionality of django-registration,
    including ``RegistrationProfile`` and its custom manager.
    
    """
    def test_new_user_is_inactive(self):
        """
        Test that a newly-created user is inactive.
        
        """
        self.failIf(self.sample_user.is_active)

    def test_registration_profile_created(self):
        """
        Test that a ``RegistrationProfile`` is created for a new user.
        
        """
        self.assertEqual(RegistrationProfile.objects.count(), 2)

    def test_activation_email(self):
        """
        Test that user signup sends an activation email.
        
        """
        self.assertEqual(len(mail.outbox), 2)

    def test_activation_email_disable(self):
        """
        Test that activation email can be disabled.

        """
        RegistrationProfile.objects.create_inactive_user(username='noemail',
                                                         password='foo',
                                                         email='nobody@example.com',
                                                         send_email=False)
        self.assertEqual(len(mail.outbox), 2)

    def test_activation(self):
        """
        Test that user activation actually activates the user and
        properly resets the activation key, and fails for an
        already-active or expired user, or an invalid key.
        
        """
        # Activating a valid user returns the user.
        self.failUnlessEqual(RegistrationProfile.objects.activate_user(RegistrationProfile.objects.get(user=self.sample_user).activation_key).pk,
                             self.sample_user.pk)
        
        # The activated user must now be active.
        self.failUnless(User.objects.get(pk=self.sample_user.pk).is_active)
        
        # The activation key must now be reset to the "already activated" constant.
        self.failUnlessEqual(RegistrationProfile.objects.get(user=self.sample_user).activation_key,
                             RegistrationProfile.ACTIVATED)
        
        # Activating an expired user returns False.
        self.failIf(RegistrationProfile.objects.activate_user(RegistrationProfile.objects.get(user=self.expired_user).activation_key))
        
        # Activating from a key that isn't a SHA1 hash returns False.
        self.failIf(RegistrationProfile.objects.activate_user('foo'))
        
        # Activating from a key that doesn't exist returns False.
        self.failIf(RegistrationProfile.objects.activate_user(sha.new('foo').hexdigest()))

    def test_account_expiration_condition(self):
        """
        Test that ``RegistrationProfile.activation_key_expired()``
        returns ``True`` for expired users and for active users, and
        ``False`` otherwise.
        
        """
        # Unexpired user returns False.
        self.failIf(RegistrationProfile.objects.get(user=self.sample_user).activation_key_expired())

        # Expired user returns True.
        self.failUnless(RegistrationProfile.objects.get(user=self.expired_user).activation_key_expired())

        # Activated user returns True.
        RegistrationProfile.objects.activate_user(RegistrationProfile.objects.get(user=self.sample_user).activation_key)
        self.failUnless(RegistrationProfile.objects.get(user=self.sample_user).activation_key_expired())

    def test_expired_user_deletion(self):
        """
        Test that
        ``RegistrationProfile.objects.delete_expired_users()`` deletes
        only inactive users whose activation window has expired.
        
        """
        RegistrationProfile.objects.delete_expired_users()
        self.assertEqual(RegistrationProfile.objects.count(), 1)

    def test_management_command(self):
        """
        Test that ``manage.py cleanupregistration`` functions
        correctly.
        
        """
        management.call_command('cleanupregistration')
        self.assertEqual(RegistrationProfile.objects.count(), 1)

    def test_signals(self):
        """
        Test that the ``user_registered`` and ``user_activated``
        signals are sent, and that they send the ``User`` as an
        argument.
        
        """
        def receiver(sender, **kwargs):
            self.assert_('user' in kwargs)
            self.assertEqual(kwargs['user'].username, u'signal_test')
            received_signals.append(kwargs.get('signal'))

        received_signals = []
        expected_signals = [signals.user_registered, signals.user_activated]
        for signal in expected_signals:
            signal.connect(receiver)

        RegistrationProfile.objects.create_inactive_user(username='signal_test',
                                                         password='foo',
                                                         email='nobody@example.com',
                                                         send_email=False)
        RegistrationProfile.objects.activate_user(RegistrationProfile.objects.get(user__username='signal_test').activation_key)

        self.assertEqual(received_signals, expected_signals)


class RegistrationFormTests(RegistrationTestCase):
    """
    Tests for the forms and custom validation logic included in
    django-registration.
    
    """

    fixtures = ['test_codes.json',]
    
    def test_registration_form(self):
        """
        Test that ``RegistrationForm`` enforces username constraints
        and matching passwords.
        
        """
        invalid_data_dicts = [
            # Non-alphanumeric username.
            {
            'data':
            { 'username': 'foo/bar',
              'email': 'foo@example.com',
              'password1': 'foo',
              'password2': 'foo',
              'agree_to_tos': 'on',},             
            'error':
            ('username', [u"Enter a valid value."])
            },
            # Already-existing username.
            {
            'data':
            { 'username': 'alice',
              'email': 'alice@example.com',
              'password1': 'secret',
              'password2': 'secret',
              'agree_to_tos': 'on', },
            'error':
            ('username', [u"This username is already taken. Please choose another."])
            },
            # Mismatched passwords.
            {
            'data':
            { 'username': 'foo',
              'email': 'foo@example.com',
              'password1': 'foo',
              'password2': 'bar',
              'agree_to_tos': 'on', },
            'error':
            ('__all__', [u"You must type the same password each time"])
            },
            # Must agree to TOS
            {
            'data':
            { 'username': 'foo',
              'email': 'foo@example.com',
              'password1': 'foo',
              'password2': 'foo',
              'agree_to_tos': False, },
            'error':
            ('agree_to_tos', [u"You must agree to the terms to register"])
            },
            
            ]

        for invalid_dict in invalid_data_dicts:
            form = forms.RegistrationForm(data=invalid_dict['data'])
            self.failIf(form.is_valid())
            self.assertEqual(form.errors[invalid_dict['error'][0]], invalid_dict['error'][1])

        form = forms.RegistrationForm(data={ 'username': 'foo',
                                             'email': 'foo@example.com',
                                             'password1': 'foo',
                                             'password2': 'foo',
                                             'agree_to_tos':'on',
                                             'promo_code':'12345678'})
        self.failUnless(form.is_valid())

    
class RegistrationViewTests(RegistrationTestCase):
    """
    Tests for the views included in django-registration.
    
    """
    def _test_registration_view(self):
        """
        Underscored to prevent running while free accounts are prohibited 
        
        Test that the registration view rejects invalid submissions,
        and creates a new user and redirects after a valid submission.
        
        """
        # Invalid data fails.
        response = self.client.post(reverse('registration_register'),
                                    data={ 'username': 'alice', # Will fail on username uniqueness.
                                           'email': 'foo@example.com',
                                           'password1': 'foo',
                                           'password2': 'foo' })
        self.assertEqual(response.status_code, 200)
        self.failUnless(response.context[0]['form'])
        self.failUnless(response.context[0]['form'].errors)

        response = self.client.post(reverse('registration_register'),
                                    data={ 'username': 'foo',
                                           'email': 'foo@example.com',
                                           'password1': 'foo',
                                           'password2': 'foo',
                                           'agree_to_tos':'on'})
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'registration/check_inbox.html')
                
        self.assertEqual(RegistrationProfile.objects.count(), 3)
    
    def test_activation_view(self):
        """
        Test that the activation view activates the user from a valid
        key and fails if the key is invalid or has expired.
       
        """
        # Valid user puts the user account into the context.
        response = self.client.get(reverse('registration_activate',
                                           kwargs={ 'activation_key': RegistrationProfile.objects.get(user=self.sample_user).activation_key }))
        self.assertEqual(response.status_code, 200)
        
        self.assertEqual(response.context[0]['account'].pk, self.sample_user.pk)

        # Expired user sets the account to False.
        response = self.client.get(reverse('registration_activate',
                                           kwargs={ 'activation_key': RegistrationProfile.objects.get(user=self.expired_user).activation_key }))
        self.assertEqual(response.status_code, 404)

        # Invalid key gets to the view, but sets account to False.
        response = self.client.get(reverse('registration_activate',
                                           kwargs={ 'activation_key': 'foo' }))
        # hmmm, need an assertion here

        # Nonexistent key sets the account to False.
        response = self.client.get(reverse('registration_activate',
                                           kwargs={ 'activation_key': sha.new('foo').hexdigest() }))
        self.assertEqual(response.status_code, 404)
