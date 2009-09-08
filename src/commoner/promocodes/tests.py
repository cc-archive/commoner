# tests for commoner.promocodes
from datetime import date, datetime

from django.test import TestCase
from django.core.urlresolvers import reverse

from commoner.profiles.models import CommonerProfile
from commoner.registration.models import RegistrationProfile
from commoner.promocodes.models import PromoCode
from commoner.promocodes.forms import PromoCodeField


class TestPromoCodeRegistration(TestCase):
    """ Testing the functionality of promo codes at the
    user registration form.
    """
    
    fixtures = ['initial_data.json',
                'test_users.json',
                'test_codes.json',]    

    def _default_form_data(self, **kwargs):
        defaults = {
            'username':'test',
            'email':'test@example.com',
            'password1':'test',
            'password2':'test',
            'agree_to_tos':'on',
            'promo_code':'12345678'
        }
        defaults.update(kwargs)
        return defaults
    
    def test_valid_promo_code_registration(self):
        """ Positive acceptance of a valid promo code.
        Verify that the registration is premium and that the
        CommonerProfile created is a premium level profile.
        """

        form_data = self._default_form_data(promo_code='12345678')
    
        response = self.client.post(reverse("registration_register"),
                                    data=form_data)

        # the form was valid?
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/check_inbox.html')

        reg = RegistrationProfile.objects.latest('id')
        
        # check the premium property of the most recent registration
        self.failUnless(reg.premium)

        # verify the promo code has been marked as used
        promo = PromoCode.objects.get(code__exact='12345678')
        self.failUnless(promo.used)

    def test_invalid_promo_code_registration(self):
        """ Attempting to use an invalid code should trigger a
        form validation error. """

        form_data = self._default_form_data(promo_code='FAKEcode')
        
        response = self.client.post(reverse("registration_register"),
                                    data=form_data)

        self.assertEqual(response.status_code, 200)
        self.failUnless(response.context[0]['form'])
        self.assertEqual(response.context[0]['form'].errors['promo_code'][0],
                         PromoCodeField.errors['invalid_code'])
        
    def test_used_promo_code_registration(self):
        """ Attempting to register with a used code should produce
        a form error """

        form_data = self._default_form_data(promo_code='abcdefgh')
    
        response = self.client.post(reverse("registration_register"),
                                    data=form_data)

        self.assertEqual(response.status_code, 200)
        self.failUnless(response.context[0]['form'])
        self.assertEqual(response.context[0]['form'].errors['promo_code'][0],
                         PromoCodeField.errors['already_used'])

    def test_premium_profile_creation(self):

        data = {
            'username':'test',
            'email':'test@example.com',
            'password':'test',
            'promo':'abcdefgh'
        }
        
        user = RegistrationProfile.objects.create_inactive_user(**data)
        user = RegistrationProfile.objects.activate_user(
            user.registrationprofile_set.all()[0].activation_key)
                
        # get the test user that was just activated
        profile = user.get_profile()
        
        self.failUnless(profile)

        # test model properties
        self.assertFalse(profile.free)
        self.assert_(profile.premium)

        # test the expires field
        self.assert_(profile.expires.date() ==
                     date.today().replace(date.today().year + 1))
        
        # test actual level field
        self.assertEqual(profile.level, CommonerProfile.PREMIUM)
        
class TestPromoCodeRenewals(TestCase):
    """
    using a promo code to upgrade an account to a premium level
    """
    
    fixtures = ['initial_data.json', 'test_users.json', 'test_codes.json',]

    def _create_and_activate_user(self, **kwargs):
        
        data = {
            'username':'test',
            'email':'test@example.com',
            'password':'test',
            'promo':'abcdefgh',
        }

        data.update(kwargs)
        
        user = RegistrationProfile.objects.create_inactive_user(**data)
        user = RegistrationProfile.objects.activate_user(
            user.registrationprofile_set.all()[0].activation_key)
        return user
    
    def test_account_renewal(self):
        """
        Submit a promo code to renew an account.
        """

        user = self._create_and_activate_user()

        profile = user.get_profile()
        profile.expires = datetime.now()
        profile.save()

        self.assertFalse(profile.active)
        self.assertFalse(profile.free)

        # this is still a premium account
        self.assert_(profile.premium)

        PromoCode.objects.mark_as_used('12345678', user)
        
        self.assert_(profile.renew())
        
        profile.save()

        self.assert_(profile.active)
        self.assert_(profile.premium)

        # expires should now be year from today
        self.assertEquals(profile.expires.date(),
                     date.today().replace(date.today().year + 1))

    def test_account_upgrade_redirects_based_on_level(self):
        """
        If a premium user trys to access the upgrade page they
        should be redirected to the renew url, and vice verse.
        """

        user = self._create_and_activate_user()
        
        self.client.login(username='test', password='test')

        response = self.client.get('/a/upgrade/')
        self.assertRedirects(response, '/a/renew/')

        # create a FREE user
        user = self._create_and_activate_user(username='testee', promo=None)
        self.client.login(username='testee', password='test')

        response = self.client.get('/a/renew/')
        self.assertRedirects(response, '/a/upgrade/')
        
    def test_account_renewal_form(self):
        """
        When a premium user submits a promo code, their profile should 
        be renewed.
        """

        user = self._create_and_activate_user()

        self.client.login(username='test', password='test')
        response = self.client.get('/a/renew/')
        self.assertEquals(response.status_code, 200)

        original_expiration = user.get_profile().expires
        
        response = self.client.post('/a/renew/', dict(promo='12345678'))
        
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'premium/upgrade_success.html')
        self.assertFalse(response.context[0]['upgraded'])

        self.assert_(response.context[0]['profile'])
        self.assert_(response.context[0]['profile'].active)
        self.assert_(response.context[0]['profile'].premium)
        self.assertEquals(response.context[0]['profile'].expires,
                     original_expiration.replace(original_expiration.year + 1))
        
        
    def test_account_upgrade_form(self):
        """
        When a free user submits a promo code, their profile should be
        upgrade to a premium level and their expiration be set a year in
        advance.
        """

        # create a FREE user
        user = self._create_and_activate_user(username='testee', promo=None)

        self.assert_(user.get_profile().free)
        
        self.client.login(username='testee', password='test')

        response = self.client.get('/a/upgrade/')
        self.assertEquals(response.status_code, 200)

        response = self.client.post('/a/renew/', dict(promo='12345678'))
        
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'premium/upgrade_success.html')
        self.assert_(response.context[0]['upgraded'])

        self.assert_(response.context[0]['profile'])
        self.assert_(response.context[0]['profile'].active)
        self.assert_(response.context[0]['profile'].premium)
        self.assertEquals(response.context[0]['profile'].expires.date(),
                     date.today().replace(date.today().year + 1))
        
        
        
        
            
            
        
        
