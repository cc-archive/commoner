# Code sampled from Stephen Zabel - sjzabel@gmail.com

from django.conf import settings
from django.http import HttpResponsePermanentRedirect, get_host

class SSLMiddleware:
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        secure = request.is_secure()
        if not secure:
            
            try:
                profile = request.user.get_profile()
            except ObjectDoesNotExist:
                profile = None
            
            if profile.redirect_https:
                newurl = "https://%s%s" % (get_host(request),request.get_full_path())
            
                if settings.DEBUG and request.method == 'POST':
                    raise RuntimeError, \
                        """Django can't perform a SSL redirect while maintaining POST data.
                           Please structure your views so that redirects only occur during GETs."""
            
                return HttpResponsePermanentRedirect(newurl)
