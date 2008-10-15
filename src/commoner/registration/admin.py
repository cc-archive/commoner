from django.contrib import admin
from commoner.registration.models import PartialRegistration
from django.utils.translation import ugettext_lazy as _

class PartialRegistrationAdmin(admin.ModelAdmin):

    list_display = ('email', 'last_name', 'first_name', 'transaction_id')
    search_fields = ('email', 'last_name', 'first_name', 'transaction_id')
    list_filter = ('complete',)

    fieldsets = (
        (None, {
	    'fields':('last_name', 'first_name', 'email', 'complete', 'transaction_id', 'user'),
	    'description':_('Adding a new registration will send a welcome email.')},
	),
	)

    def save_model(self, request, obj, form, change):
        obj.save()

        if not change:
	    # creating a new instance
	    PartialRegistration.objects.send_welcome(obj)

admin.site.register(PartialRegistration, PartialRegistrationAdmin)
