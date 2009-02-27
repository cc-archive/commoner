from django.contrib import admin
from commoner.broadcast.models import SimpleAlert, RobustAlert

class SimpleAlertAdmin(admin.ModelAdmin):
    list_display = ['author', 'message', 'date_created']

class RobustAlertAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'start_date', 'end_date', 'enabled']

admin.site.register(SimpleAlert, SimpleAlertAdmin)
admin.site.register(RobustAlert, RobustAlertAdmin)
