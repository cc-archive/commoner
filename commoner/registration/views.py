from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from forms import CompleteRegistrationForm

from models import PartialRegistration

def complete(request, key):

    # make sure this is a valid registration key
    try:
        partial = PartialRegistration.objects.get(key__exact = key)
    except PartialRegistration.DoesNotExist:
        raise Http404

    if request.method == 'POST':
        # process an attempt to complete the registration
        form = CompleteRegistrationForm(partial, data=request.POST)
        if form.is_valid():
            new_user = form.save()

            return HttpResponseRedirect('/a/register/complete/')
    else:
        form = CompleteRegistrationForm(partial)
    
    context = RequestContext(request)
    return render_to_response('registration/complete_registration.html',
                              { 'form': form },
                              context_instance=context)
