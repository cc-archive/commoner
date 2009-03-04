from django.contrib import admin
from commoner.broadcast.models import Alert, Message

class AlertAdmin(admin.ModelAdmin):
    list_display = ['author', 'message', 'date_created']

class MessageAdmin(admin.ModelAdmin):
    list_display = ['title', 'start_date', 'end_date','ack_req', 'enabled']

admin.site.register(Alert, AlertAdmin)
admin.site.register(Message, MessageAdmin)
