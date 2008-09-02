from django.contrib import admin
from commoner.registration.models import PartialRegistration

class PartialRegistrationAdmin(admin.ModelAdmin):

    pass

admin.site.register(PartialRegistration, PartialRegistrationAdmin)
