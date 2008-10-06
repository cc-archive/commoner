import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'commoner.settings'

import commoner.content.models as content
import commoner.works.models as works

if __name__ == '__main__':

    for c in content.Content.objects.all():

        # create a new registration
        reg = works.Registration(owner=c.user,
                                 created=c.registered)
        reg.save()

        work = works.Work(registration=reg,
                          url=c.url,
                          title=c.title,
                          license_url=c.license,
                          registered=c.registered)
        work.save()


