from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _

from paypal.standard.forms import PayPalPaymentsForm

from commoner.premium.models import PromoCode

from forms import RegistrationForm
from models import Registration 

def activate(request, key):

    user = Registration.objects.activate_user(key)

    if user is None:
        raise Http404
    
    return HttpResponseRedirect('/a/register/complete/')

def create(request):
    
    """ Creating a free acount """
    
    # check if the user is logged in
    if request.user.is_authenticated():
        request.user.message_set.create(
            message=_(u"Please log out before creating a new account."))
        return HttpResponseRedirect(
            reverse('profile_view', args=(request.user.username,)))
    
    if request.method == 'POST':
        
        form = RegistrationForm(data=request.POST)
        if form.is_valid():
            
            registration = form.save()

            # record the usage of the promo code
            if form.cleaned_data.get('promo_code', False):
                promo = PromoCode(form.cleaned_data['promo_code'])
                promo.used_by = registration.user
                promo.save()
            
            return render_to_response('registration/check_inbox.html')
    else:
        
        form = RegistrationForm()
    
    return render_to_response('registration/complete_registration.html',
                                {'form':form}, 
                                context_instance=RequestContext(request))

@login_required                                
def upgrade(request):
    
    """ Upgrade account page. """
    
    try:
        profile = request.user.get_profile()
    except ObjectDoesNotExist:
        profile = models.CommonerProfile(user=request.user)
        
    student_paypal_dict = {
        "business": "johndo_1246911637_biz@gmail.com",
        "amount": "25.00",
        "item_name": "CC Network Account",
        "invoice": "unique-invoice-id",
        "notify_url": "http://www.example.com/your-ipn-location/",
        "return_url": "http://www.example.com/your-return-location/",
        "cancel_return": "http://www.example.com/your-cancel-location/",
    }
    
    normal_paypal_dict = dict(**student_paypal_dict)
    normal_paypal_dict['amount'] = "50.00"
    
    # Create the instance.
    student_form = PayPalPaymentsForm(initial=student_paypal_dict)
    normal_form = PayPalPaymentsForm(initial=normal_paypal_dict)

    return render_to_response('registration/upgrade.html', {   
            'profile': profile, 
            'student_form': student_form, 
            'normal_form': normal_form 
        }, context_instance=RequestContext(request)
    )
    
