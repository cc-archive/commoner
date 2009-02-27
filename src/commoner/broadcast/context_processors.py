from django.conf import settings
from django.contrib.auth.decorators import login_required
from commoner.broadcast.models import RobustAlert, AlertLog

@login_required
def messages(request):
    # get all alerts for the day
    alerts = RobustAlert.active.all()
    site_messages = []
    for alert in alerts:
        # get all logs of this alert for this user
        log = AlertLog.objects.filter(user=request.user, alert=alert)
        
        if log.count() < alert.view_limit:
            # if the alert is to be shown once per session then restrict view
            show = True
            if alert.per_session:
                show = log.filter(session=request.session.session_key).count() == 0
            if show:    
                # add message to the context and log table
                site_messages.append(alert.content)
                AlertLog(
                    user = request.user, 
                    alert = alert, 
                    session = request.session.session_key
                ).save()
    # this needs to be changed to something other than 
    # 'messages' and added to template logic    
    return {'site_messages':site_messages}