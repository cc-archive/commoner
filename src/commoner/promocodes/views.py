try:
    import json
except:
    import simplejson as json
    
import hashlib
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.views.generic.simple import direct_to_template
from django.conf import settings

from commoner.profiles.models import CommonerProfile
from commoner.promocodes.forms import PremiumUpgradeForm 

import models

def invite(request):
    """ Accepts a POST request and transmits an invitation letter and
    code to the recipient who made the contribution """

    if request.method != 'POST': # respond w/ 500 (415 may be more prudent)
        return HttpResponseServerError('Method unavailable')

    # POST should carry a JSON string and an HMAC 
    try:
        # throws KeyError's
        data = request.POST['data']
        hmac = request.POST['hash']

        auth_hash = hashlib.sha1()
        # might want to create another secret for this purpose
        auth_hash.update(settings.INVITE_KEY) 
        auth_hash.update(str(data))
        
        assert auth_hash.hexdigest() == str(hmac) # POST var's are unicode
        
    except:
        return HttpResponseServerError('Cannot verify authenticity of data')

    try:
        contrib = json.loads(data)
                
        if not models.PromoCode.objects.contribution_is_unique(
            contrib['id'], contrib['contribution_recur_id']):
            return HttpResponseServerError(
                'Invitation already created')

        if not models.PromoCode.objects.contribution_is_sufficient(
            contrib['amount'], bool(contrib['contribution_recur_id'])):
            return HttpResponseServerError('Insufficient amount')
        
        code = models.PromoCode.objects.create_promo_code(
            email=unicode(contrib['email']),
            trxn_id=unicode(contrib['trxn_id']),
            contrib_id=int(contrib['id']),
            recurring_id=int(contrib['contribution_recur_id']),
            send_email=bool(contrib['send']),
            )

        return HttpResponse(json.dumps(
            dict(url=reverse('redeem_code', args=[code]))
            ))
        
    except Exception, e:
        return HttpResponseServerError('Invalid data: %s' % e)

@login_required
def account_upgrade(request):

    profile = request.user.get_profile()
    
    """ Process the upgrade form submissions. """
            
    if request.method == "POST":

        form = PremiumUpgradeForm(data=request.POST)

        if form.is_valid():

            promo_code = form.save()
            
            promo = models.PromoCode.objects.mark_as_used(code=xpromo_code.code,
                                                   user=request.user)

            upgrading = profile.free
            
            if upgrading:
                profile.upgrade()
            else:
                profile.renew()
                
            profile.save()
            
            # render to a page detailing what just happened and how long their
            # premium membership will last.
                        
            return render_to_response("promocodes/apply_success.html",
                                      {'profile':profile, 'upgraded':upgrading},
                                      context_instance=RequestContext(request))
            
    else:

        # since we share this view with two urls (/a/upgrade + /a/renew)
        # it may be worthwhile to check the profile type of the user and
        # redirect free profiles from /a/renew -> /a/upgrade and vice versa.

        param_string = ""
        if 'c' in request.GET:
            param_string = "?c=%s" % request.GET['c']        
        
        if profile.free and request.path == reverse('account_renew_complete'):
            return HttpResponseRedirect(reverse('account_upgrade_complete') + param_string)
        elif not profile.free and request.path == reverse('account_upgrade_complete'):
            return HttpResponseRedirect(reverse('account_renew_complete') + param_string)

        form = PremiumUpgradeForm()

        # autofill the promo code it the url contains one
        if 'c' in request.GET:  
            form.fields['promo'].initial = request.GET['c']
            
    return render_to_response("promocodes/apply_code.html",
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
            return HttpResponseRedirect('/a/upgrade/complete/?c=%s' % code)
        else:
            return HttpResponseRedirect('/a/renew/complete/?c=%s' % code)
    
    return render_to_response("promocodes/redeem_code.html", {'code':code},
                              context_instance=RequestContext(request))

