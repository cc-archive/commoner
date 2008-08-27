
from django.conf.urls.defaults import patterns, include, handler500
from django.conf import settings

from django.contrib import admin

handler500 # Pyflakes

admin.autodiscover()

urlpatterns = patterns(
    '',
    (r'^$', 'django.views.generic.simple.direct_to_template',
     {'template':'index.html'}),
    (r'^admin/(.*)', admin.site.root),
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^accounts/', include('registration.urls')),
    (r'^p/', include('profiles.urls')),

    (r'^c/(?P<content_id>\d+)/$', 
        'commoner.profiles.views.content_detail'),
    )

urlpatterns += patterns(
    'commoner.server.views',
    (r'^xrds/$', 'idpXrds'),
    (r'^processTrustResult/$', 'processTrustResult'),
    # (r'^user/$', 'idPage'),
    (r'^endpoint/$', 'endpoint'),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', 
         {'document_root': settings.MEDIA_ROOT}),
    )
