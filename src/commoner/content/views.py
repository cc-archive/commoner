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
        instance = get_object_or_404(models.Content, id=id)

        # make sure the instance user is actually the owner
        if instance.user != request.user:
            return HttpResponseForbidden("Forbidden.")

    else:
        instance = None

    if request.method == 'POST':
        # process the form
        form = forms.ContentForm(data=request.POST, instance=instance)

        if form.is_valid():
            content = form.save(commit=False)
            content.user = request.user
            content.save()

            return HttpResponseRedirect(
                reverse('profile_view', args=(request.user.username,)))

    else:
        # just display the form
        form = forms.ContentForm(instance=instance)
        
    return render_to_response('content/edit.html',
                              { 'form': form,
                                'content': instance
                                },
                              context_instance=RequestContext(request)
                              )

@login_required
def delete(request, id):

    instance = get_object_or_404(models.Content, id=id)

    if instance.user != request.user:
        return HttpResponseForbidden("Forbidden.")

    if request.method == 'POST':
        # process the form
        form = forms.ContentDeleteForm(data=request.POST)

        if form.is_valid():

            if form.cleaned_data['confirm_delete']:
                # remove the content object
                instance.delete()

            # redirect to the profile
            return HttpResponseRedirect(
                reverse('profile_view', args=(request.user.username,)))

    else:
        # just display the form
        form = forms.ContentDeleteForm()
        
    return render_to_response('content/delete.html',
                              { 'form': form,
                                'content': instance
                                },
                              context_instance=RequestContext(request)
                              )

def view(request, id):

    work = get_object_or_404(models.Content, id=id)

    return render_to_response('content/view.html',
                              dict(work=work),
                              context_instance=RequestContext(request))

def by_uri(request):

    uri = request.GET.get('uri', None)

    works = models.Content.objects.filter(url = uri)

    if len(works) == 1:
        return HttpResponseRedirect(
            reverse('view_work', args=(works[0].id,)))
    elif len(works) == 0:
        # not found
        raise Http404("No works matched the given URL, %s" % uri)
    

    # display the disambiguation list
    return render_to_response('content/list.html',
                              dict(works=works,
                                   message="More than one work matches the URL provided.",
                                   ),
                              context_instance=RequestContext(request))

