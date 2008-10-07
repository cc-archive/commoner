from commoner.works import models

import django.test 

class WorkFormTestCase(django.test.TestCase):
    fixtures = ['test_users.json', ]

        
    def test_add_globbing_work(self):

        # log in as the "normal" user
        self.client.login(username='normal', password='testing')

        # retrieve the add page
        response = self.client.get('/w/add/')
        self.assertEqual(response.status_code, 200)

        # post a new work
        response = self.client.post('/w/add/', 
                                    dict(title='Test Glob Adding',
                                         url='http://example.org/test/glob/adding',
                                         license_url='http://example.org/license',
                                         claim_all=True))

        # make sure we were redirected
        self.assertEqual(response.status_code, 302)

        # retrieve the last created work
        work = list(models.Work.objects.filter(
                registration__owner__username = 'normal').all())[-1]

        # verify the constraint was created correctly
        self.assert_(work.is_simple_glob())

    def test_edit_globbing_work(self):


        # log in as the "normal" user
        self.client.login(username='normal', password='testing')

        # retrieve the add page
        response = self.client.get('/w/add/')
        self.assertEqual(response.status_code, 200)

        # post a new work
        response = self.client.post('/w/add/', 
                                    dict(title='Test Glob Adding',
                                         url='http://example.org/test/glob/adding',
                                         license_url='http://example.org/license',
                                         claim_all=True))

        # make sure we were redirected
        self.assertEqual(response.status_code, 302)

        # retrieve the last created work
        work = list(models.Work.objects.filter(
                registration__owner__username = 'normal').all())[-1]

        # verify the constraint was created correctly
        self.assert_(work.is_simple_glob())

        # edit the work
        response = self.client.get('/w/%s/edit/' % work.id)
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/w/%s/edit/' % work.id,
                                    dict(title = 'Test Glob Editing',
                                         url='http://example.org/glob/editing',
                                         license_url='http://example.org/license',
                                         claim_all='on'),)
        self.assertEqual(response.status_code, 302)

        # verify the edit was successful
        edited_work = models.Work.objects.get(id=work.id)
        self.assertEqual(edited_work.title, 'Test Glob Editing')

        # make sure the constraint is correctly added
        self.assertEqual(edited_work.constraints.all()[0].value, 
                         edited_work.url)
