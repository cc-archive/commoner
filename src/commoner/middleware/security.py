from django.conf import settings
from django.http import HttpResponsePermanentRedirect, HttpResponseForbidden, get_host
from django.core.exceptions import ObjectDoesNotExist, MiddlewareNotUsed
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from commoner.profiles.views import view as view_profile

class SSLMiddleware:
    
    def __init__(self):
        if settings.TESTING:
            raise MiddlewareNotUsed
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        
        # only perform on HTTP
        if not request.is_secure():
            
            # user is attempting to view profile
            if view_func is view_profile:
                
                # get the requested user
                user = get_object_or_404(User, username=view_kwargs['username'])
                try:
                    profile = user.get_profile()
                except ObjectDoesNotExist:
                    profile = models.CommonerProfile(user=user)
                
                # if the user is not legacy then refuse to allow http access
                if profile.redirect_https:
                    return HttpResponseForbidden('<h1>Forbidden</h1>This key is invalid, use https.')
                else:
                    request.session['from_http'] = True
         
            # forward the user to https
            newurl = "https://%s%s" % (get_host(request),request.get_full_path())
            return HttpResponsePermanentRedirect(newurl)
    
    #TODO - get the process response to work correctly!
    def process_response(self, request, response):
        
        # check if from_http cookie is set
        if request.session.get('from_http', False):
            request.session['from_http'] = False
        
        return response
