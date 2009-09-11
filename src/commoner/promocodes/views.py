from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.views.generic.simple import direct_to_template

from commoner.profiles.models import CommonerProfile
from commoner.promocodes.forms import PremiumUpgradeForm 

import models

@login_required
def account_upgrade(request):

    profile = request.user.get_profile()
    
    """ Process the upgrade form submissions. """
            
    if request.method == "POST":

        form = PremiumUpgradeForm(data=request.POST)

        if form.is_valid():

            promo_code = form.save()
            
            promo = models.PromoCode.objects.mark_as_used(code=promo_code.code,
                                                   user=request.user)

            upgrading = profile.free
            
            if upgrading:
                profile.upgrade()
            else:
                profile.renew()
                
            profile.save()
            
            # render to a page detailing what just happened and how long their
            # premium membership will last.
                        
            return render_to_response("promocodes/upgrade_success.html",
                                      {'profile':profile, 'upgraded':upgrading},
                                      context_instance=RequestContext(request))
            
    else:

        # since we share this view with two urls (/a/upgrade + /a/renew)
        # it may be worthwhile to check the profile type of the user and
        # redirect free profiles from /a/renew -> /a/upgrade and vice versa.

        param_string = ""
        if 'c' in request.GET:
            param_string = "?c=%s" % request.GET['c']        
        
        if profile.free and request.path == reverse('account_renew'):
            return HttpResponseRedirect(reverse('account_upgrade') + param_string)
        elif not profile.free and request.path == reverse('account_upgrade'):
            return HttpResponseRedirect(reverse('account_renew') + param_string)

        form = PremiumUpgradeForm()

        # autofill the promo code it the url contains one
        if 'c' in request.GET:  
            form.fields['promo'].initial = request.GET['c']
            
    return render_to_response("promocodes/account_upgrade.html",
                              {'form':form, 'profile':profile, },
                              context_instance=RequestContext(request))
        

@login_required
def account_overview(request):

    return render_to_response('promocodes/account_overview.html',
                              {'profile':request.user.get_profile()},
                              context_instance=RequestContext(request))

def redeem_code(request, code=None):

    # if the user is logged in, then redirect them
    if request.user.is_authenticated():
        profile = request.user.get_profile()
        if profile.free:
            return HttpResponseRedirect('/a/upgrade/?c=%s' % code)
        else:
            return HttpResponseRedirect('/a/renew/?c=%s' % code)
    
    return render_to_response("promocodes/redeem_code.html", {'code':code},
                              context_instance=RequestContext(request))

