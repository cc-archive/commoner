from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
from django.core import mail

import forms

def contact(request):

    if request.method == 'POST':
        form = forms.ContactForm(request.POST)
        if form.is_valid(): 

            mail.send_mail(form.cleaned_data['subject'], 
                           form.cleaned_data['message'], 
                           form.cleaned_data['sender'],
                           [m[1] for m in settings.MANAGERS])
                           
            return HttpResponseRedirect('/h/contact/thanks/') 

    else:
        form = forms.ContactForm() 

    return render_to_response('help/contact.html', 
                              dict(form=form),
                              context_instance = RequestContext(request))

