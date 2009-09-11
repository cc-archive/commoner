import django.test 
from commoner.works import models

class TestSecurity(django.test.TestCase):
    fixtures = ['test_users.json','test_profiles.json',]

    def test_edit_security(self):

        # log in as "normal" and create a work
        self.client.login(username='normal', password='testing')
        response = self.client.post('/r/add/', 
                                    dict(title='Test Work',
                                         url='http://example.org/test/work',
                                         license_url='http://creativecommons.org/licenses/by/3.0/'))

        # make sure we were redirected
        self.assertEqual(response.status_code, 302)

        # XXX make sure we were redirected to the profile...

        # get the new work ID
        work_id = models.Work.objects.filter(registration__owner__username = 'normal').all()[0].id

        # we created the object; we can view the edit page
        response = self.client.get('/r/%s/edit/' % work_id)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/r/%s/delete/' % work_id)
        self.assertEqual(response.status_code, 200)

        # logout
        self.client.logout()

        # log in as "testing" and retrieve the work page
        self.client.login(username='testing', password='testing')

        # attempt to edit the work and make sure we are 403-Forbidden
        response = self.client.get('/r/%s/edit/' % work_id)
        self.assertEqual(response.status_code, 403)

    def test_delete_security(self):

        # log in as "normal" and create a work
        self.client.login(username='normal', password='testing')
        response = self.client.post('/r/add/', 
                                    dict(title='Test Work',
                                         url='http://example.org/test/work',
                                         license_url='http://creativecommons.org/licenses/by/3.0/'))

        # make sure we were redirected
        self.assertEqual(response.status_code, 302)

        # XXX make sure we were redirected to the profile...

        # get the new work ID
        work_id = models.Work.objects.filter(registration__owner__username = 'normal').all()[0].id

        # we created the object; we can view the delete page
        response = self.client.get('/r/%s/delete/' % work_id)
        self.assertEqual(response.status_code, 200)

        # logout
        self.client.logout()

        # log in as "testing" and retrieve the work page
        self.client.login(username='testing', password='testing')

        # attempt to delete the work and make sure we are 403-Forbidden
        response = self.client.get('/r/%s/delete/' % work_id)
        self.assertEqual(response.status_code, 403)
