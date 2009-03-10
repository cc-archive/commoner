from django.conf import settings
from django.http import HttpResponsePermanentRedirect, get_host
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from commoner.profiles.views import view as view_profile

class SSLMiddleware:
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        
        if not request.is_secure():
            
            if view_func is view_profile:
                user = get_object_or_404(User, username=view_kwargs['username'])
                try:
                    profile = user.get_profile()
                except ObjectDoesNotExist:
                    profile = models.CommonerProfile(user=user)
                if not profile.redirect_https:
                    return
                    
            newurl = "https://%s%s" % (get_host(request),request.get_full_path())
            
            return HttpResponsePermanentRedirect(newurl)
