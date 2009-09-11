import django.test 
from commoner.works import models

class TestLookup(django.test.TestCase):
    fixtures = ['test_users.json', 'test_profiles.json', ]

    def setUp(self):
        """Set up the test database for the lookup tests."""

        self.client.login(username='normal', password='testing')

        response = self.client.post('/r/add/', 
                                    dict(title='One',
                                         url='http://example.org/test/work/1',
                                         license_url='http://creativecommons.org/licenses/by/3.0/'),)
        self.assertEqual(response.status_code, 302)

        response = self.client.post('/r/add/', 
                                    dict(title='Two',
                                         url='http://example.org/test/work/2',
                                         license_url='http://creativecommons.org/licenses/by/3.0/'))
        self.assertEqual(response.status_code, 302)

    def test_by_uri(self):
        """Test work lookup by exact URI."""

        response = self.client.get('/r/lookup/', {'uri':'http://example.org/test/work/1'})

        self.assertRedirects(response, '/r/1/')

    def test_multi_match_lookup(self):
        """Test looking up a URL with may match multiple works."""

        response = self.client.get('/r/lookup/', {'uri':'http://example.org/test/work/'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The following matching works")

    def test_failed_lookup(self):
        """Test looking up a URL that is not registered."""

        response = self.client.get('/r/lookup/',{'uri':'http://example.com/test'})
        self.assertEqual(response.status_code, 404)
        self.assert_('No works found' in response.content)
