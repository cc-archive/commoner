from django.contrib import admin
from commoner.registration.models import PartialRegistration

class PartialRegistrationAdmin(admin.ModelAdmin):

    list_filter = ('complete',)

admin.site.register(PartialRegistration, PartialRegistrationAdmin)
