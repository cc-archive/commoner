from django.contrib import admin
from commoner.registration.models import PartialRegistration

class PartialRegistrationAdmin(admin.ModelAdmin):

    list_filter = ('complete',)

    fieldsets = (
        (None, {
	    'fields':('last_name', 'first_name', 'email', 'complete', 'transaction_id', 'user'),
	    'description':'Adding a new registration will send a welcome email.'},
	),
	)

    def save_model(self, request, obj, form, change):
        obj.save()

        if not change:
	    # creating a new instance
	    PartialRegistration.objects.send_welcome(obj)

admin.site.register(PartialRegistration, PartialRegistrationAdmin)
