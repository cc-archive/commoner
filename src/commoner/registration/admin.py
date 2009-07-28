from django.contrib import admin
from commoner.registration.models import Registration
from django.utils.translation import ugettext_lazy as _

class RegistrationAdmin(admin.ModelAdmin):

    list_display = ('user', 'key')
    
    def save_model(self, request, obj, form, change):
        obj.save()

        if not change:
	    # creating a new instance
	    Registration.objects.send_activation(obj)

admin.site.register(Registration, RegistrationAdmin)
