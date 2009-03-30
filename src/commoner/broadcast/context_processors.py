from django.conf import settings
from django.contrib.auth.decorators import login_required
from commoner.broadcast.models import Message, Log

def messages(request):
    
    if request.user.is_authenticated():
        
        messages = Message.active.all()
        site_messages = []
        
        for message in messages:
            
            try:
                
                # it exists in the log
                log = Log.objects.get(user=request.user, message=message)
                
                # the user hasn't acked
                if message.ack_req and not log.acked:
                    # show the alert
                    site_messages.append(message)
                    
            except:
                
                site_messages.append(message)
                Log(
                    user = request.user, 
                    message = message, 
                    acked = False
                ).save()
        
        return {'site_messages' : site_messages}
    
    else:
        return {}