from django.conf.urls.defaults import patterns, url, handler500
from django.conf import settings

from django.contrib import admin

import views

handler500 # Pyflakes

admin.autodiscover()

urlpatterns = patterns(
    'commoner.profiles',
    
    url(r'^edit/$',
        views.edit_profile, name='profile_edit'),
    url(r'^create/$',
        views.create_profile, name='profile_create'),

    url(r'^(?P<username>\w+)/$',
        views.profile_view, name='profile_view'),
    )
