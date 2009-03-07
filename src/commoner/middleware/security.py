__license__ = "Python"
__copyright__ = "Copyright (C) 2007, Stephen Zabel"
__author__ = "Stephen Zabel - sjzabel@gmail.com"
__contributors__ = "Jay Parlar - parlar@gmail.com"

from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse, HttpResponsePermanentRedirect, get_host

SSL = 'SSL'

class SSLMiddleware:
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        secure = request.is_secure()
        if not secure:
            newurl = "https://%s%s" % (get_host(request),request.get_full_path())
            if settings.DEBUG and request.method == 'POST':
                raise RuntimeError, \
                    """Django can't perform a SSL redirect while maintaining POST data.
                       Please structure your views so that redirects only occur during GETs."""
            
            return HttpResponsePermanentRedirect(newurl)
