from django.contrib import admin
from commoner.profiles.models import CommonerProfile

class CommonerProfileAdmin(admin.ModelAdmin):
    pass

admin.site.register(CommonerProfile, CommonerProfileAdmin)
