from django.conf.urls.defaults import patterns, include, handler500, handler404, url
from django.conf import settings

from django.contrib import admin

urlpatterns = patterns(
    '',

    # Badge view
    url(r'^p/(?P<username>\w+)/$', 'commoner_i.views.badge',
        name='profile_badge'),

    # chiclet badget view
    url(r'^p/(?P<username>\w+)/80x15/$', 'commoner_i.views.badge',
        {'size':'/80x15'},
        name='profile_badge'),


)
