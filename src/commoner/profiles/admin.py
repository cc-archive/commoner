from django.contrib import admin
from commoner.profiles.models import CommonerProfile

class CommonerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'level', 'nickname', 'gratis', 'expires')

admin.site.register(CommonerProfile, CommonerProfileAdmin)
