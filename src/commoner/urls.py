
from django.conf.urls.defaults import patterns, include, handler500, url
from django.conf import settings

from django.contrib import admin

handler500 # Pyflakes

admin.autodiscover()

urlpatterns = patterns(
    '',
    (r'^$', 'django.views.generic.simple.direct_to_template',
     {'template':'index.html'}),
    (r'^admin/(.*)', admin.site.root),

    # Account management
    (r'^a/login/$', 'django.contrib.auth.views.login'),
    (r'^a/logout/$', 'django.contrib.auth.views.logout'),
    (r'^a/register/complete/$', 
     'django.views.generic.simple.direct_to_template',
     {'template':'registration/success.html'}),
    (r'^a/register/(?P<key>\w+)/', 'commoner.registration.views.complete'),

    # Profile management
    url(r'^p/edit/$', 'commoner.profiles.views.edit_profile', 
        name='profile_edit'),
    url(r'^p/create/$', 'commoner.profiles.views.create_profile', 
        name='profile_create'),

    # Content management
    url(r'^(?P<username>\w+)/content/add/', 
        'commoner.content.views.add_or_edit',
        name='add_content'),
    url(r'^(?P<username>\w+)/content/edit/(?P<id>\d+)/', 
        'commoner.content.views.add_or_edit',
        name='edit_content'),
    url(r'^(?P<username>\w+)/content/delete/(?P<id>\d+)/', 
        'commoner.content.views.delete',
        name='delete_content'),
    
    # OpenID Support
    (r'^o/xrds/$', 'commoner.server.views.idpXrds'),
    (r'^o/processTrustResult/$', 'commoner.server.views.processTrustResult'),
    (r'^o/endpoint/$', 'commoner.server.views.endpoint'),

    # Profile view
    url(r'^(?P<username>\w+)/$', 'commoner.profiles.views.profile_view',
        name='profile_view'),
    (r'^(?P<username>\w+)$', 'django.views.generic.simple.redirect_to',
        {'url':'/%(username)s/'}),

)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', 
         {'document_root': settings.MEDIA_ROOT}),
    )
