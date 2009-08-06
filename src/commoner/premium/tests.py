# tests for commoner.premium

from django.test import TestCase

from django.core.urlresolvers import reverse

from commoner.profiles.models import CommonerProfile
from commoner.registration.models import RegistrationProfile
from commoner.premium.models import PromoCode
from commoner.premium.forms import PromoCodeField


class TestPromoCodeRegistration(TestCase):
    """ Testing the functionality of promo codes at the
    user registration form.
    """
    
    fixtures = ['initial_data.json',
                'test_users.json',
                'test_codes.json',]    
    
    def test_valid_promo_code_registration(self):
        """ Positive acceptance of a valid promo code.
        Verify that the registration is premium and that the
        CommonerProfile created is a premium level profile.
        """

        form_data = {
            'username':'test',
            'email':'test@example.com',
            'password1':'test',
            'password2':'test',
            'agree_to_tos':'on',
            'first_name':'test',
            'last_name':'test',
            'promo_code':'12345678'
        }

        response = self.client.post(reverse("registration_register"),
                                    data=form_data)

        # the form was valid?
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/check_inbox.html')

        # check the premium property of the most recent registration
        self.failUnless(RegistrationProfile.objects.latest('id').premium)

        # verify the promo code has been marked as used
        promo = PromoCode.objects.get(code__exact='12345678')
        self.failUnless(promo.used)

    def test_invalid_promo_code_registration(self):
        """ Attempting to use an invalid code should trigger a
        form validation error. """

        form_data = {
            'username':'test',
            'email':'test@example.com',
            'password1':'test',
            'password2':'test',
            'agree_to_tos':'on',
            'first_name':'test',
            'last_name':'test',
            'promo_code':'FAKEcode'
        }

        response = self.client.post(reverse("registration_register"),
                                    data=form_data)

        self.assertEqual(response.status_code, 200)
        self.failUnless(response.context[0]['form'])
        self.assertEqual(response.context[0]['form'].errors['promo_code'][0],
                         PromoCodeField.errors['invalid_code'])
        
    def test_used_promo_code_registration(self):
        """ Attempting to register with a used code should produce
        a form error """

        form_data = {
            'username':'test',
            'email':'test@example.com',
            'password1':'test',
            'password2':'test',
            'agree_to_tos':'on',
            'first_name':'test',
            'last_name':'test',
            'promo_code':'abcdefgh'
        }

        response = self.client.post(reverse("registration_register"),
                                    data=form_data)

        self.assertEqual(response.status_code, 200)
        self.failUnless(response.context[0]['form'])
        self.assertEqual(response.context[0]['form'].errors['promo_code'][0],
                         PromoCodeField.errors['already_used'])

    def test_premium_profile_creation(self):

        # run the valid promo code test
        self.test_valid_promo_code_registration()

        reg = RegistrationProfile.objects.latest('id')

        # activate user
        response = self.client.get(reverse('registration_activate',
                                           kwargs={ 'activation_key':reg.activation_key }))
        self.assertEqual(response.status_code, 200)

        # get the test user that was just activated
        profile = reg.user.get_profile()
        
        self.failUnless(profile)

        # test property method
        self.assertFalse(profile.free)
        # test actual level field
        self.assertEqual(profile.level, CommonerProfile.PREMIUM)
        

        
        
