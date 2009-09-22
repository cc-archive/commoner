from django.contrib import admin
from commoner.profiles.models import CommonerProfile

def make_gratis(modeladmin, request, queryset):
    queryset.update(gratis=True)
make_gratis.short_description = "Mark selected profiles as gratis"

class CommonerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'level', 'nickname', 'gratis', 'expires')
    search_fields = ('user__username', 'user__email', 
                     'user__first_name', 'user__last_name')
    list_filter = ('gratis', 'level')

    actions = [make_gratis]

admin.site.register(CommonerProfile, CommonerProfileAdmin)
