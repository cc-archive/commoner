import django.test 
from commoner.works import models

class TestEditing(django.test.TestCase):
    fixtures = ['test_users.json', ]
        
    def test_add_work(self):

        # log in as the "normal" user
        self.client.login(username='normal', password='testing')

        # retrieve the add page
        response = self.client.get('/r/add/')
        self.assertEqual(response.status_code, 200)

        # post a new work
        response = self.client.post('/r/add/', 
                                    dict(title='Test Work Adding',
                                         url='http://example.org/test/work/adding',
                                         license_url='http://creativecommons.org/licenses/by/3.0/'))

        # make sure we were redirected
        self.assertEqual(response.status_code, 302)

        # retrieve the last created work
        work = list(models.Work.objects.filter(
                registration__owner__username = 'normal').all())[-1]

        # verify it exists
        self.assertEqual(work.url, 'http://example.org/test/work/adding')
        self.assertEqual(work.title, 'Test Work Adding')
        self.assertEqual(work.license_url, 'http://creativecommons.org/licenses/by/3.0/')

    def test_edit_work(self):

        # log in as the "normal" user
        self.client.login(username='normal', password='testing')

        # retrieve the add page
        response = self.client.get('/r/add/')
        self.assertEqual(response.status_code, 200)

        # post a new work
        response = self.client.post('/r/add/', 
                                    dict(title='Test Work Adding',
                                         url='http://example.org/test/work/adding',
                                         license_url='http://creativecommons.org/licenses/by/3.0/'))

        # make sure we were redirected
        self.assertEqual(response.status_code, 302)

        # retrieve the last created work
        work_id = list(models.Work.objects.filter(
                registration__owner__username = 'normal').all())[-1].id

        # edit the work
        response = self.client.get('/r/%s/edit/' % work_id)
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/r/%s/edit/' % work_id,
                                    dict(title = 'Test Work Editing',
                                         url='http://example.org/test/work/adding',
                                         license_url='http://example.org/license'))
        self.assertEqual(response.status_code, 302)

        # verify the edit was successful
        work = models.Work.objects.get(id=work_id)
        self.assertEqual(work.title, 'Test Work Editing')
        self.assertEqual(work.license_url, 'http://example.org/license')

    def test_delete_work(self):

        # log in as the "normal" user
        self.client.login(username='normal', password='testing')

        # retrieve the add page
        response = self.client.get('/r/add/')
        self.assertEqual(response.status_code, 200)

        # post a new work
        response = self.client.post('/r/add/', 
                                    dict(title='Test Work Adding',
                                         url='http://example.org/test/work/deleting',
                                         license_url='http://creativecommons.org/licenses/by/3.0/'))

        # make sure we were redirected
        self.assertEqual(response.status_code, 302)

        # retrieve the last created work
        work = list(models.Work.objects.filter(
                registration__owner__username = 'normal').all())[-1]

        # verify it exists
        self.assertEqual(work.url, 'http://example.org/test/work/deleting')
        self.assertEqual(work.title, 'Test Work Adding')
        self.assertEqual(work.license_url, 'http://creativecommons.org/licenses/by/3.0/')

        # now delete it
        work_id = work.id
        del work
        response = self.client.get('/r/%s/delete/' % work_id)
        response = self.client.post('/r/%s/delete/' % work_id,
                                    dict(confirm=True))
        self.assertEqual(response.status_code, 302)

        # verify it no longer exists
        self.assertRaises(models.Work.DoesNotExist, models.Work.objects.get,
                          id=work_id)
