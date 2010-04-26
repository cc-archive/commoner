# tests for commoner.promocodes
from datetime import date, datetime

try:
    import json
except ImportError:
    import simplejson as json
from hashlib import sha1
import itertools

from django.test import TestCase
from django.core import mail
from django.conf import settings
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

    def test_redeem_redirects_to_renew(self):
        """ Verify that the /a/redeem/codecode view redirects appropriately for
        the different user levels """
        
        user = self._create_and_activate_user()

        # user is not logged in, so both options should be presented
        response = self.client.get("/a/redeem/abcdefgh/")
        self.assertTemplateUsed(response, "promocodes/redeem_code.html")

        # ensure that if the user is authenticated that a 302 occurs
        self.client.login(username='test', password='test')
        response = self.client.get("/a/redeem/abcdefgh/")
        self.assertRedirects(response, "/a/renew/complete/?c=abcdefgh")

        # ensure if the user is free, then it should 302 to upgrade
        user = self._create_and_activate_user(username='testee', promo=None)
        self.assert_(user.get_profile().free)
        self.client.login(username='testee', password='test')
        response = self.client.get("/a/redeem/abcdefgh/")
        self.assertRedirects(response, "/a/upgrade/complete/?c=abcdefgh")

    def test_promocode_GET_var_populates_textfields(self):
        """ renew/?c=codecode and upgrade/?c=codecode should default the
        promo code textfield to that value. """

        user = self._create_and_activate_user()
        self.client.login(username='test', password='test')
        
        response = self.client.get("/a/renew/complete/?c=abcdefgh")
        self.assert_(response.context[0]['form'].fields['promo'].initial == 'abcdefgh')

        user = self._create_and_activate_user(username='testee', promo=None)
        self.client.login(username='testee', password='test')

        response = self.client.get("/a/upgrade/complete/?c=abcdefgh")
        self.assert_(response.context[0]['form'].fields['promo'].initial == 'abcdefgh')

    def test_promo_code_creation(self):
        """ Ensure that the manager method produces valid promo codes and
        properly delivers email messages. """

        # using just an email
        promocode = PromoCode.objects.create_promo_code('test@example.com')
        self.assert_(not promocode.used)
        self.assertEquals(len(mail.outbox), 1)
        self.assert_('test@example.com' in mail.outbox[0].to)
        self.assertEquals(mail.outbox[0].subject, 'Registration Link for the Creative Commons Network')
        self.assert_(('redeem/%s' % promocode) in mail.outbox[0].body)

        # assert paypal and civi information is store when supplied
        promocode = PromoCode.objects.create_promo_code('test@example.com', 'paypal_id', '123')
        self.assertEquals(promocode.transaction_id, 'paypal_id')
        self.assertEquals(promocode.contribution_id, '123') #civi contrib row id

        # should support no email at all for batch creationm
        promocode = PromoCode.objects.create_promo_code()
        self.assert_(not promocode.used)
        
        
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

        response = self.client.get('/a/upgrade/complete/')
        self.assertRedirects(response, '/a/renew/complete/')

        # create a FREE user
        user = self._create_and_activate_user(username='testee', promo=None)
        self.client.login(username='testee', password='test')

        response = self.client.get('/a/renew/complete/')
        self.assertRedirects(response, '/a/upgrade/complete/')
        
    def test_account_renewal_form(self):
        """
        When a premium user submits a promo code, their profile should 
        be renewed.
        """

        user = self._create_and_activate_user()

        self.client.login(username='test', password='test')
        response = self.client.get('/a/renew/complete/')
        self.assertEquals(response.status_code, 200)

        original_expiration = user.get_profile().expires
        
        response = self.client.post('/a/renew/complete/', dict(promo='12345678'))
        
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'promocodes/apply_success.html')
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

        response = self.client.get('/a/upgrade/complete/')
        self.assertEquals(response.status_code, 200)

        response = self.client.post('/a/renew/complete/', dict(promo='12345678'))
        
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'promocodes/apply_success.html')
        self.assert_(response.context[0]['upgraded'])

        self.assert_(response.context[0]['profile'])
        self.assert_(response.context[0]['profile'].active)
        self.assert_(response.context[0]['profile'].premium)
        self.assertEquals(response.context[0]['profile'].expires.date(),
                     date.today().replace(date.today().year + 1))
        
class TestInvites(TestCase):

    def _gen_hmac(self, key, data):

        sha_hash = sha1()
        sha_hash.update(key)
        sha_hash.update(data)

        return sha_hash.hexdigest()

    def setUp(self):

        self.data = json.dumps({
            'email' : 'test@example.com',
            'trxn_id': 100,
            'amount': settings.INVITE_AMOUNT,
            'contribution_recur_id': 0,
            'id': 1000,
            'send': True
            })

        self.hmac = self._gen_hmac(settings.INVITE_KEY, self.data)
        
    def test_200_invite_response(self):
        """ Verify that successful invitations respond with 200 status code """
        
        r = self.client.post('/a/invite/',
                             {'data': self.data, 'hash': self.hmac})

        code = PromoCode.objects.latest('pk')
                
        self.assertEquals(r.status_code, 200)
        self.assertEquals(r.content, '{"url": "/a/redeem/%s/"}' % code)
        self.assertEquals(len(mail.outbox), 1)
        

    def test_500_duplicate(self):
        """ Only one invite can be generate for a contribution """
        r = self.client.post('/a/invite/',
                             {'data': self.data, 'hash': self.hmac})

        code = PromoCode.objects.latest('pk')
        
        self.assertEquals(r.status_code, 200)
        self.assertEquals(r.content, '{"url": "/a/redeem/%s/"}' % code)
        self.assertEquals(len(mail.outbox), 1)

        # should fail on duplicate contribution
        r = self.client.post('/a/invite/',
                             {'data': self.data, 'hash': self.hmac})
        self.assertEquals(r.status_code, 500)
        self.assertEquals(r.content, 'Invitation already created')
        self.assertEquals(len(mail.outbox), 1) # one 1 message sent for this test case

    def test_500_invalid_hmac(self):
        """ Invalid hash keys return 500 response """
        r = self.client.post('/a/invite/',
                             {'data': self.data, 'hash': '1234567890abcdef'})
        self.assertEquals(r.status_code, 500)
        self.assertEquals(r.content, 'Cannot verify authenticity of data')
        self.assertEquals(len(mail.outbox), 0) # one 1 message sent for this test case

    def test_500_only_POST_support(self):
        """ Non-POST requests result in 500 responses """

        r = self.client.get('/a/invite/')
        self.assertEquals(r.status_code, 500)
        self.assertEquals(r.content, 'Method unavailable')

    def test_all_parameters_required(self):
        """ Fails if 'hash' or 'data' are not in the POST-data """

        r = self.client.post('/a/invite/',
                             {'data': self.data })
        self.assertEquals(r.status_code, 500)
        self.assertEquals(r.content, 'Cannot verify authenticity of data')


        r = self.client.post('/a/invite/',
                             {'hash': self.hmac })
        self.assertEquals(r.status_code, 500)
        self.assertEquals(r.content, 'Cannot verify authenticity of data')
        
        
    def test_data_required_keys(self):
        """ Fails unless all `data` keys are set """

        # generate all possible combinations of lengths 1,2,3 of
        # the 4 required params
        contrib = json.loads(self.data)
        for i in range(1,len(contrib.keys())):
            for combo in itertools.combinations(contrib.keys(), i):
                data = json.dumps(dict([(k, contrib[k]) for k in combo]))
                r = self.client.post('/a/invite/',
                                     {'hash': self._gen_hmac(settings.INVITE_KEY,data),
                                      'data': data })
            
                self.assertEquals(r.status_code, 500)
                self.assert_(r.content.startswith('Invalid data'))

    def test_contrib_id_is_number(self):
        """ Fail unless the id is None or an Integer """

        data = json.loads(self.data)
        data['id'] = 'testing'
        data = json.dumps(data)
        hmac = self._gen_hmac(settings.INVITE_KEY,data)

        r = self.client.post('/a/invite/', {'data': data, 'hash': hmac})
        self.assertEquals(r.status_code, 500)
        self.assert_(r.content.startswith('Invalid data'))

        # string integers are acceptable
        data = json.loads(self.data)
        data['id'] = '110'
        data = json.dumps(data)
        hmac = self._gen_hmac(settings.INVITE_KEY,data)

        r = self.client.post('/a/invite/', {'data': data, 'hash': hmac})
        self.assertEquals(r.status_code, 200)
        
        
    def test_insufficient_amount(self):
        """ Fail for contributions below invitation amount. """

        data = json.loads(self.data)
        data['amount'] = settings.INVITE_AMOUNT - 10 # subtract 10 bucks
        data = json.dumps(data)
        hmac = self._gen_hmac(settings.INVITE_KEY,data)

        r = self.client.post('/a/invite/', {'data': data, 'hash': hmac})
        self.assertEquals(r.status_code, 500)
        self.assert_(r.content.startswith('Insufficient amount'))

    def test_recurring_contributions_amount(self):
        """ Verify that recurring contributions generate invitations. """
        
        data = json.loads(self.data)
        data['contribution_recur_id'] = 42
        data['amount'] = settings.INVITE_AMOUNT / 12 
        data = json.dumps(data)
        hmac = self._gen_hmac(settings.INVITE_KEY,data)
        
        r = self.client.post('/a/invite/', {'data': data, 'hash': hmac})
        self.assertEquals(r.status_code, 200)

        data = json.loads(self.data)
        data['id'] = 1001 # looks new 
        data['contribution_recur_id'] = 42 # part as same contrib as above
        data['amount'] = settings.INVITE_AMOUNT / 12 
        data = json.dumps(data)
        hmac = self._gen_hmac(settings.INVITE_KEY,data)

        r = self.client.post('/a/invite/', {'data': data, 'hash': hmac})
        self.assertEquals(r.status_code, 500)
        self.assertEquals(r.content, 'Invitation already created')


