from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseForbidden
from django.utils.translation import ugettext as _
import models

def premium_required(func):
    """ 
    Restrict free users from views
    If the user doesn not pass the test, then the decorated view is never called
    and the request is redirected to a 500.
    This code works as an extension of the auth.login_required decorator
    """
    
    @wraps(func)
    def _decorator(request, *args, **kwargs):
    
        # should we check for login? or trust that the login_required was called
        # prior to this decorator? I vote for checking authentication here. -JED3
    
        #login_required(func)    
    
        # if eval gets here, then the user is not anonymous 
        try:
            profile = request.user.get_profile()
        
        except ObjectDoesNotExist:
        
            profile = models.CommonerProfile(user=request.user)
       
        if profile.free or not profile.active:
        
            return HttpResponseForbidden(_("You do not have access to this page."))
    
        return func(request, *args, **kwargs)
    
    return _decorator
