
from django.conf.urls.defaults import patterns, include, handler500, handler404, url
from django.conf import settings

from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns(
    '',
    (r'^$', 'django.views.generic.simple.direct_to_template',
     {'template':'index.html'}),
    (r'^admin/(.*)', admin.site.root),
    
	# Help pages
    (r'^h/about/$', 'django.views.generic.simple.direct_to_template',
	 {'template':'help/about.html'}),
	(r'^h/openid/$', 'django.views.generic.simple.direct_to_template',
	 {'template':'help/openid.html'}),
    (r'^h/privacy/$', 'django.views.generic.simple.direct_to_template',
	 {'template':'help/privacy.html'}),

    # Account management
    (r'^a/login/$', 'django.contrib.auth.views.login'),
    (r'^a/logout/$', 'django.contrib.auth.views.logout',
     {'template_name':'registration/logout.html'}),

    url(r'^a/password/change/$',
        'django.contrib.auth.views.password_change',
        name='password_change'),
    url(r'^a/password/change/done/$',
        'django.contrib.auth.views.password_change_done',),
    url(r'^a/password/reset/$',
        'django.contrib.auth.views.password_reset',
        name='password_reset'),
    url(r'^a/password/reset/done/$',
        'django.contrib.auth.views.password_reset_done',),

    (r'^a/register/complete/$', 
     'django.views.generic.simple.direct_to_template',
     {'template':'registration/success.html'}),
    (r'^a/register/(?P<key>\w+)/', 'commoner.registration.views.complete'),

    # Profile management
    url(r'^p/edit/$', 'commoner.profiles.views.edit_or_create', 
        name='profile_edit'),

    # Work management
    url(r'^w/add/', 
        'commoner.content.views.add_or_edit',
        name='add_content'),
    url(r'^w/(?P<id>\d+)/edit/', 
        'commoner.content.views.add_or_edit',
        name='edit_content'),
    url(r'^w/(?P<id>\d+)/delete/', 
        'commoner.content.views.delete',
        name='delete_content'),
    url(r'^w/lookup/$', 'commoner.content.views.by_uri',
        name='lookup_work'),
    url(r'^w/(?P<id>\d+)/', 'commoner.content.views.view',
        name='view_work'),
    
    # OpenID Support
    (r'^o/xrds/$', 'commoner.server.views.idpXrds'),
    (r'^o/processTrustResult/$', 'commoner.server.views.processTrustResult'),
    (r'^o/endpoint/$', 'commoner.server.views.endpoint'),

    # RDF 
    url(r'^r/all.rdf$', 'commoner.profiles.views.all_rdf',
        name='all_rdf'),

    # Profile views
    url(r'^(?P<username>\w+)/works/$', 'commoner.profiles.views.works',
        name='profile_works'),
    url(r'^(?P<username>\w+)/works/rdf$', 'commoner.profiles.views.user_rdf',
        name='profile_works'),
    url(r'^(?P<username>\w+)/$', 'commoner.profiles.views.view',
        name='profile_view'),
    (r'^(?P<username>\w+)$', 'django.views.generic.simple.redirect_to',
        {'url':'/%(username)s/'}),

)

if False :
    #settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', 
         {'document_root': settings.MEDIA_ROOT}),
    )
