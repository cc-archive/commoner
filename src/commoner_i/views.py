from django.core.files.storage import default_storage
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.http import HttpResponse


def badge(request, username):

    # get a handle for the user profile
    profile = get_object_or_404(User, username=username)
    profile = profile.get_profile()

    # serve the inactive badge by default
    filename = 'm/images/badge/inactive.png'

    if profile.active:
        # serve the active badge
        filename = 'm/images/badge/active.png'


    # set the content type appropriately
    return HttpResponse(default_storage.open(filename).read(),
                        content_type='image/png')
