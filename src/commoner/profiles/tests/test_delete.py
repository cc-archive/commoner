import django.test 

from django.contrib import auth
from commoner.profiles import models

class TestDelete(django.test.TestCase):
    fixtures = ['test_users.json', ]

    def test_anonymous_delete(self):
        """Attempting to delete your account when not logged in should
        result in a 403."""

        response = self.client.get('/a/delete/')
        self.assertEquals(response.status_code, 403)

    def test_delete_no_profile(self):
        """Delete a user with no profile attached."""

        self.client.login(username='testing', password='testing')

        response = self.client.get('/a/delete/')
        self.assertContains(response, "Are you sure you wish to continue?")

        # confirm deletion of the profile
        response = self.client.post('/a/delete/', dict(confirm='Yes, delete'))
        self.assertEquals(response.status_code, 200)

        # make sure the user no longer exists
        self.assertRaises(auth.models.User.DoesNotExist,
                          auth.models.User.objects.get, username='testing')

    def test_delete_with_profile(self):
        """Deleting a user who has a profile should also delete the 
        profile object."""

        self.client.login(username='normal', password='testing')

        # confirm deletion of the profile
        response = self.client.post('/a/delete/', dict(confirm='Yes, delete'))
        self.assertEquals(response.status_code, 200)

        # the Profile no longer exists...
        self.assertRaises(models.CommonerProfile.DoesNotExist,
                          models.CommonerProfile.objects.get, 
                          user__username='normal')

        # ...and neither does the User
        self.assertRaises(auth.models.User.DoesNotExist,
                          auth.models.User.objects.get, username='normal')
