from django.contrib.sites.models import Site, RequestSite
from django.http import Http404, HttpResponseRedirect, HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import get_object_or_404, render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext
from django.core.urlresolvers import reverse

from django.utils.translation import ugettext as _
from django.conf import settings
from django.views.decorators.cache import never_cache
from django.contrib import auth

from commoner import util

import forms

def login(request, template_name='registration/login.html', 
          redirect_field_name=auth.REDIRECT_FIELD_NAME):
    "Displays the login form and handles the login action."

    # get the page to redirect to after login;
    redirect_to = request.REQUEST.get(redirect_field_name, None)

    if redirect_to is None:
        # fall back to the referrer if no redirection is specified
        redirect_to = request.META.get('HTTP_REFERER', '')
        if redirect_to:
            # make sure we were redirected from our own domain
            base_url = util.getBaseURL(request)
            if redirect_to.find(base_url) == 0 \
                and not redirect_to.find("logout"):
                redirect_to = redirect_to[len(base_url) - 1:]
            else:
                redirect_to = ""

    if request.method == "POST":
        form = forms.LoginForm(data=request.POST)
        if form.is_valid():
            # Light security check -- make sure redirect_to isn't garbage.
            if not redirect_to or '//' in redirect_to or ' ' in redirect_to:
                redirect_to = settings.LOGIN_REDIRECT_URL
            from django.contrib.auth import login
            login(request, form.get_user())
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()

            # see if the user wants to be remembered
            if form.cleaned_data['remember']:
                request.session.set_expiry(settings.SESSION_COOKIE_AGE)

            return HttpResponseRedirect(redirect_to)
    else:
        form = forms.LoginForm(request)
    request.session.set_test_cookie()
    if Site._meta.installed:
        current_site = Site.objects.get_current()
    else:
        current_site = RequestSite(request)
    return render_to_response(template_name, {
        'form': form,
        redirect_field_name: redirect_to,
        'site_name': current_site.name,
        }, context_instance=RequestContext(request))
login = never_cache(login)

def logout(request, template_name='registration/logout.html'):
    """Log the user out."""

    auth.logout(request)

    return render_to_response(template_name, {},
                              context_instance=RequestContext(request))
