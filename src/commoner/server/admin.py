from django.contrib import admin
from commoner.server.models import TrustedRelyingParty, TrustedMetadata

class TrustedMetadataAdmin(admin.TabularInline):
    model = TrustedMetadata

class TrustedRelyingPartyAdmin(admin.ModelAdmin):
    list_display = ('user', 'root')
    inlines = [TrustedMetadataAdmin]

admin.site.register(TrustedRelyingParty,
                    TrustedRelyingPartyAdmin)
