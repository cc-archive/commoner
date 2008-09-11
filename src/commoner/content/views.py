from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse

import forms
import models

@login_required
def add_or_edit(request, id=None):

    if id is not None:
        instance = models.Content.objects.get(id=id)
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
