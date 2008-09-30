from django.contrib import admin
from commoner.profiles.models import CommonerProfile

class CommonerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'expires')
    date_hierarchy = 'expires'

admin.site.register(CommonerProfile, CommonerProfileAdmin)
