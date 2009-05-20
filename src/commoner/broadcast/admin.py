from django.contrib import admin
from django import forms
from commoner.broadcast.models import Alert, Message

class AlertAdmin(admin.ModelAdmin):
    list_display = ['author', 'message', 'date_created']

class MessageAdminForm(forms.ModelForm):
    class Meta:
        model = Message
    
    def clean(self):
        data = self.cleaned_data
        
        if data.get('end_date') is None:
            
            if not data.get('ack_req'):
               raise forms.ValidationError(
                    "If the message does not require acknowledgment, \
                    then you must specify an end date.")
                    
        return data

class MessageAdmin(admin.ModelAdmin):
    list_display = ['title', 'start_date', 'end_date','ack_req', 'enabled']
    form = MessageAdminForm

admin.site.register(Alert, AlertAdmin)
admin.site.register(Message, MessageAdmin)
