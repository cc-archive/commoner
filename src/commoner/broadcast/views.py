from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.conf import settings

from commoner.broadcast.models import Log

@login_required
def ack(request, message_id):
    
    user = request.user
    
    if user.is_anonymous():
        raise HttpResponseForbidden("You must be logged in to perform this action.")
        
    else:
        # if the alert doesnt exist in the log, then that means the user has not seen it yet
        # and therefore cannot acknowledge it before reading the message
        log = get_object_or_404(Log, user=user, message__id=message_id)
        log.acked = True
        log.save()
        
        redirect_to = request.META.get('HTTP_REFERER', '')
        
        # if no referrer is supplied then redirect to default redirect view
        if not redirect_to or ' ' in redirect_to:
            redirect_to = reverse(settings.LOGIN_REDIRECT_VIEW, args=[user.username])
            
        return HttpResponseRedirect(redirect_to)
