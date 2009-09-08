from django.core.files.storage import default_storage
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.http import HttpResponse, Http404

def badge(request, username, size=''):

    # serve the inactive badge by default
    filename = 'images/badge/%sinactive.png' % size

    # get a handle for the user profile
    profile = get_object_or_404(User, username=username)
    profile = profile.get_profile()

    if profile.free:
        # return a 404 for FREE profiles
        raise Http404
    
    if profile.active:
        # serve the active badge
        filename = 'images/badge%s/active.png' % size

    # set the content type appropriately
    return HttpResponse(default_storage.open(filename).read(),
                        content_type='image/png')
