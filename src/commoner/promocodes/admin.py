from django.contrib import admin
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms.widgets import HiddenInput

from commoner.promocodes.models import PromoCode

class PromoCodeAdminForm(forms.ModelForm):

    code = forms.CharField(initial='', widget=HiddenInput())
    send_email = forms.BooleanField(label=_(u'Send invitation letter?'), required=False)
    
    def __init__(self, *args, **kwargs):
        # if not done here, unique_code_string is only loaded when admin is bootstrapped
        if 'instance' not in kwargs:
            kwargs['initial'] = {'code': PromoCode.objects.unique_code_string()}
        super(PromoCodeAdminForm, self).__init__(*args, **kwargs)

    def save(self, force_insert=False, force_update=False, commit=True):
        
        code = super(PromoCodeAdminForm, self).save(commit)
                
        if self.cleaned_data['send_email']:
            PromoCode.objects.send_invite_letter(code)

        return code

    class Meta:
        model = PromoCode

class PromoCodeAdmin(admin.ModelAdmin):

    form = PromoCodeAdminForm
    actions = ["resend_codes"]

    list_display = ('recipient', 'code', 'created', 'used')    
    fields = ('code', 'recipient', 'expires', 'transaction_id', 'civicrm_id', 'send_email',)
    ordering = ('-created',)
    search_fields = ('recipient', 'transaction_id', 'civicrm_id',)
    date_hierarchy = 'created'
        
    # get the pretty admin boolean icons, still no filter abilities
    def used(self, object):
        return object.used
    used.short_description = _(u'Redeemed code')
    used.boolean = True


    def resend_codes(self, request, queryset):
        """Resend one or more Codes from the admin interface."""
    
        sent = 0
        already_used = 0

        for code in queryset:
            if not(code.used):
                PromoCode.objects.send_invite_letter(code)
                sent = sent + 1
            else:
                already_used = already_used + 1
        
        message = "%s code(s) sent." % sent

        if already_used:
            message = "%s %s already used, not re-sent." % (
                message, already_used)

        self.message_user(request, message)

    resend_codes.short_description = "Resend selected codes."

admin.site.register(PromoCode, PromoCodeAdmin)
