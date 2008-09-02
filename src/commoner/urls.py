
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
    (r'^a/register/(?P<key>.*)/', 'commoner.registration.views.complete'),

    # Profile management
    url(r'^p/edit/$', 'commoner.profiles.views.edit_profile', 
        name='profile_edit'),
    url(r'^p/create/$', 'commoner.profiles.views.create_profile', 
        name='profile_create'),

    # Content details
    #(r'^c/(?P<content_id>\d+)/$', 
    #    'commoner.profiles.views.content_detail'),
    
    # OpenID Support
    (r'^o/xrds/$', 'commoner.server.views.idpXrds'),
    (r'^o/processTrustResult/$', 'commoner.server.views.processTrustResult'),
    (r'^o/endpoint/$', 'commoner.server.views.endpoint'),

    # Profile view
    url(r'^(?P<username>.*)/$', 'commoner.profiles.views.profile_view',
        name='profile_view'),

)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', 
         {'document_root': settings.MEDIA_ROOT}),
    )
