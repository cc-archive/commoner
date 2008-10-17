import django.test
from django.conf import settings

class TestLogin(django.test.TestCase):
    fixtures = ['test_users.json', ]

    def testLogin(self):
        """Test logging in."""

        response = self.client.get('/a/login/')
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/a/login/', 
                                    dict(username='testing',
                                         password='testing'))
        self.assert_(self.client.session.get_expire_at_browser_close())

        # attempt to access a restricted resource
        response = self.client.get('/p/edit/')
        self.assertEqual(response.status_code, 200)

    def testLoginWithNext(self):
        """Log in and specify the page to redirect to."""

        response = self.client.post('/a/login/', 
                                    dict(username='testing',
                                         password='testing',
                                         next='/p/edit/'))
        self.assertRedirects(response, '/p/edit/')

    def testRememberMe(self):
        """Setting remember_me to True should make the cookie long-lived."""

        response = self.client.post('/a/login/', 
                                    dict(username='testing',
                                         password='testing',
                                         remember='on',
                                         ))
        self.assertRedirects(response, '/')
        self.assertEqual(self.client.session.get_expiry_age(), 
                         settings.SESSION_COOKIE_AGE)
        self.assert_(not(self.client.session.get_expire_at_browser_close()))
