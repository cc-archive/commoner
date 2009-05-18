from django.conf import settings
from django.http import HttpResponsePermanentRedirect, get_host
from django.core.exceptions import MiddlewareNotUsed

class HttpsRedirectMiddleware:
    
    def __init__(self):
        if settings.TESTING:
            raise MiddlewareNotUsed
    
    def process_view(self, request, view_func, view_args, view_kwargs):
                
        # only act on incoming HTTP
        if not request.is_secure():
                            
            # forward the user to https
            newurl = "https://%s%s" % (
                get_host(request), request.get_full_path())
            
            request.session['from_http'] = True
            
            return HttpResponsePermanentRedirect(newurl)

    def process_response(self, request, response):
        
        """ The response from the http->https redirect needs to be
        ignored, therefore two bools are used: 
            from_http is set to True when an HTTP redirect to HTTPS occurs
            from_http_redirect is set to True after the redirect has occurred
        """
        
        # check if a redirect has occurred
        if request.session.get('from_http', False):
            
            if request.session.get('from_http_redirect', False):
                
                # the process is done
                del request.session['from_http']
                del request.session['from_http_redirect']
                
            else:
                # the redirected request is being processed
                request.session['from_http_redirect'] = True
        
        return response