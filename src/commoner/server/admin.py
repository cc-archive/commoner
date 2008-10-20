from django.contrib import admin
from commoner.server.models import TrustedRelyingParty

class TrustedRelyingPartyAdmin(admin.ModelAdmin):
    list_display = ('user', 'root')

admin.site.register(TrustedRelyingParty,
                    TrustedRelyingPartyAdmin)
