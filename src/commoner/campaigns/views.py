from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from commoner.profiles.models import CommonerProfile

import forms
import models

@login_required
def edit_or_create(request):
    """ Edit or create a campaign for the given user. """
    
    # first check if they need the edit page
    try:
        campaign_obj = models.Campaign.objects.get(user=request.user)
    except ObjectDoesNotExist:
        campaign_obj = None
    
    if request.method == 'POST':
        
        form = forms.CampaignForm(request.user, data=request.POST, 
                                    instance=campaign_obj)
        
        if form.is_valid():
            
            campaign = form.save(commit=False)
            campaign.user = request.user
            campaign.save()
            
            return HttpResponseRedirect(reverse('profile_campaign', 
                                    args=(request.user.username,)))
            
    else:
        
        form = forms.CampaignForm(request.user, instance=campaign_obj)
        
    return render_to_response('campaigns/edit.html', 
                            {'campaign':campaign_obj, 
                            'form':form,
                            },
                            context_instance=RequestContext(request))
                            
def view(request, username):
    """ View the personalized campaign page for the given username """
    
    user = get_object_or_404(User, username=username)
    try:
        profile_obj = user.get_profile()
    except ObjectDoesNotExist:
        profile_obj = CommonerProfile(user=user)
    
    campaign_obj = get_object_or_404(models.Campaign, user=user)
    
    return render_to_response('campaigns/view.html', 
                            {'campaign':campaign_obj,
                            'profile':profile_obj,
                            'profile_user':user},
                            context_instance=RequestContext(request))
        
        
    
    