from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _

from forms import CompleteRegistrationForm, FreeRegistrationForm

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

def create(request):
    
    """ Creation of free accounts """
    
    # check if the user is logged in
    if request.user.is_authenticated():
        request.user.message_set.create(
            message=_(u"Please log out before creating a new account."))
        return HttpResponseRedirect(
            reverse('profile_view', args=(request.user.username,)))
    
    if request.method == 'POST':
        
        form = FreeRegistrationForm(data=request.POST)
        if form.is_valid():
            partial_reg = form.save()
            
            # need to change this behavior
            return render_to_response('registration/check_inbox.html')
    else:
        
        form = FreeRegistrationForm()
    
    return render_to_response('registration/free_registration.html',
                                {'form':form}, 
                                context_instance=RequestContext(request))