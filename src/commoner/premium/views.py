from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _

from commoner.profiles.models import CommonerProfile
from commoner.premium.forms import PremiumUpgradeForm 

@login_required
def account_upgrade(request):

    """ Process the upgrade form submissions. """

    if request.method == "POST":

        form = PremiumUpgradeForm(data=request.POST)

        if form.is_valid():

            today = datetime.now()

            # mark the promo code as used
            promo_code = form.save()
            promo_code.used_by = request.user
            promo_code.used_on = today
            promo_code.save()
            
            # update the auth'd user's profile 
            profile = request.user.get_profile()
            profile.level = CommonerProfile.PREMIUM
            profile.expires = today.replace(today.year + 1)
            profile.save()

            # render to a page detailing what just happened and how long their
            # premium membership will last.

            return render_to_response("premium/upgrade_success.html", {},
                                      context_instance=RequestContext(request))
            
    else:

        form = PremiumUpgradeForm()
        
    return render_to_response("premium/account_upgrade.html", {'form':form},
                              context_instance=RequestContext(request))
        

@login_required
def account_overview(request):
    
    profile = request.user.get_profile()
    
    return render_to_response('premium/account_overview.html', {   
            'profile': profile, 
        }, context_instance=RequestContext(request))
                     
@login_required
def purchase_upgrade(request):

    """ Paypal form for the purchasing of a promo code. """

    pass
    
