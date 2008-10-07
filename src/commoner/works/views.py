from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse

import forms
import models

@login_required
def add_or_edit(request, id=None):

    if id is not None:
        instance = get_object_or_404(models.Work, id=id)

        # make sure the instance user is actually the owner
        if instance.owner_user != request.user:
            return HttpResponseForbidden("Forbidden.")

    else:
        instance = None

    if request.method == 'POST':
        # process the form
        form = forms.SimpleRegistrationForm(
            request.user,
            instance=instance,
            data=request.POST)

        if form.is_valid():
            form.save()

            return HttpResponseRedirect(
                reverse('profile_view', args=(request.user.username,)))

    else:
        # just display the form
        form = forms.SimpleRegistrationForm(request.user,
                                            instance=instance)
        
    return render_to_response('works/edit.html',
                              { 'form': form,
                                'work': instance
                                },
                              context_instance=RequestContext(request)
                              )

@login_required
def delete(request, id):

    instance = get_object_or_404(models.Work, id=id)

    if instance.owner_user != request.user:
        return HttpResponseForbidden("Forbidden.")

    if request.method == 'POST':

        # make sure it was submitted with the confirm button
        if request.POST.get('confirm', False):

            # remove the object
            registration = instance.registration
            instance.delete()

            # if this is the last work in a non-feed registration,
            # remove the registration as well
            if not hasattr(registration, 'feed') and \
                    registration.works.count() == 0:
                registration.delete()
            
            # redirect to the profile
            return HttpResponseRedirect(
                reverse('profile_view', args=(request.user.username,)))

    # just display the form
    return render_to_response('works/delete.html',
                              { 'content': instance
                                },
                              context_instance=RequestContext(request)
                              )

def view(request, id):

    work = get_object_or_404(models.Work, id=id)

    return render_to_response('works/view.html',
                              dict(work=work),
                              context_instance=RequestContext(request))

def by_uri(request):

    uri = request.GET.get('uri', None)
    if uri is None:
        raise Http404("No work URI specified.")

    works = models.Work.objects.filter(url__exact = uri)

    if works.count() == 1:
        return HttpResponseRedirect(
            reverse('view_work', args=(works[0].id,)))
    elif works.count() == 0:
        # try a "starts with" search
        works = models.Work.objects.filter(url__istartswith = uri)

        if works.count() == 0:
            # still not found
            raise Http404("No works matched the given URL, %s" % uri)
    

    # display the disambiguation list
    return render_to_response('works/list.html',
                              dict(works=works,
                                   message="The following matching works were found:",
                                   ),
                              context_instance=RequestContext(request))

