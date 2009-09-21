from django.contrib import admin
from commoner.log.models import LogEntry

class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('message_id', 'message', 'created',)
    list_filter = ['message_id', 'created', 'content_type']
admin.site.register(LogEntry, LogEntryAdmin)
