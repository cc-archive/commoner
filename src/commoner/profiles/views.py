from django.shortcuts import render_to_response

from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.views.generic.list_detail import object_list

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

import forms
import utils

@login_required
def edit_or_create(request):
    """Edit or create the profile for the given username."""

    try:
        profile = request.user.get_profile()
    except ObjectDoesNotExist:
        profile=None

    if request.method == 'POST':
        # process the form
        form = forms.CommonerProfileForm(request.user,
            data=request.POST, files=request.FILES, instance=profile)

        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()

            return HttpResponseRedirect(
                reverse('profile_view', args=(request.user.username,)))

    else:
        # just display the form
        form = forms.CommonerProfileForm(request.user, instance=profile)

    return render_to_response('profiles/edit_profile.html',
                              { 'form': form,
                                'profile': profile },
                              context_instance=RequestContext(request)
                              )

def view(request, username, public_profile_field=None,
                   template_name='profiles/view.html'):
    """
    Detail view of a user's profile.
    
    If no profile model has been specified in the
    ``AUTH_PROFILE_MODULE`` setting,
    ``django.contrib.auth.models.SiteProfileNotAvailable`` will be
    raised.

    If the user has not yet created a profile, ``Http404`` will be
    raised.

    If a field on the profile model determines whether the profile can
    be publicly viewed, pass the name of that field (as a string) as
    the keyword argument ``public_profile_field``; that attribute will
    be checked before displaying the profile, and if it does not
    return a ``True`` value, the ``profile`` variable in the template
    will be ``None``. As a result, this field must be a
    ``BooleanField``.
    
    To specify the template to use, pass it as the keyword argument
    ``template_name``; this will default to
    :template:`profiles/profile_detail.html` if not supplied.
    
    Context:
    
        profile
            The user's profile, or ``None`` if the user's profile is
            not publicly viewable (see the note about
            ``public_profile_field`` above).
    
    Template:
    
        ``template_name`` keyword argument or
        :template:`profiles/profile_detail.html`.
    
    """
    user = get_object_or_404(User, username=username)
    try:
        profile_obj = user.get_profile()
    except ObjectDoesNotExist:
        profile_obj = None

    if public_profile_field is not None and \
       not getattr(profile_obj, public_profile_field, False):
        profile_obj = None

    return render_to_response(template_name,
                              { 'profile'  : profile_obj,
                                'profile_user' : user,
                                'username' : username},
                              context_instance=RequestContext(request))

