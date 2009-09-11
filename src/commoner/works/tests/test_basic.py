import django.test 

class TestBasics(django.test.TestCase):
    fixtures = ['test_users.json', 'test_profiles.json', ]

    def test_urls_exist(self):
        """Basic test that work views exist."""
        
        self.client.login(username='normal', password='testing')
        
        response = self.client.get('/')

        # list
        response = self.client.get('/normal/works/')
        self.assert_(response.status_code == 200)

        # add
        response = self.client.get('/r/add/')
        self.assertEqual(response.status_code,200)
