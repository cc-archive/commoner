from django.conf.urls.defaults import patterns, include, handler500, url
from django.conf import settings

from django.contrib import admin

handler500 # Pyflakes

urlpatterns = patterns(
    '',

    # Profile view
    url(r'^p/(?P<username>\w+)/$', 'commoner_i.views.badge',
        name='profile_badge'),

)
