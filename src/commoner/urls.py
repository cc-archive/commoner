from django.conf.urls.defaults import patterns, include, handler500, handler404, url
from django.conf import settings

from django.contrib import admin

import profiles
import works
from django.contrib.sitemaps import GenericSitemap

admin.autodiscover()

profile_info = dict(
    queryset = profiles.models.CommonerProfile.objects.all(),
    date_field = 'updated',
    )
work_info = dict(
    queryset = works.models.Work.objects.all(),
    date_field = 'updated',
    )

sitemaps = {
    'profiles':GenericSitemap(profile_info, priority=0.75,
                              changefreq='weekly'),
    'works':GenericSitemap(work_info, priority=1.0,
                           changefreq='weekly'),
    }

urlpatterns = patterns(
    '',
    (r'^$', 'django.views.generic.simple.direct_to_template',
     {'template':'index.html'}),
    (r'^seatbeltcfg.xml$', 'django.views.generic.simple.direct_to_template',
     {'template':'seatbeltcfg.xml', 'mimetype':'text/xml'}),
    (r'^admin/(.*)', admin.site.root),
    
    url(r'^sitemap.xml', 'django.contrib.sitemaps.views.sitemap',
     {'sitemaps':sitemaps}, name='sitemap_xml'),
    (r'^robots.txt', 'django.views.generic.simple.direct_to_template',
     {'template':'robots.txt', 'mimetype':'text/plain'}),
    
    # Help pages
    (r'^h/about/$', 'django.views.generic.simple.direct_to_template',
	 {'template':'help/about.html'}),
    (r'^h/openid/$', 'django.views.generic.simple.direct_to_template',
	 {'template':'help/openid.html'}),
    (r'^h/privacy/$', 'django.views.generic.simple.direct_to_template',
	 {'template':'help/privacy.html'}),
    url(r'^h/contact/$', 'commoner.help.views.contact',
        name='contact_form'),
    (r'^h/contact/thanks/$', 'django.views.generic.simple.direct_to_template',
	 {'template':'help/contact_thanks.html'}),

    # Account management
    url(r'^a/login/$', 'commoner.authenticate.views.login',
        name='login'),
    url(r'^a/logout/$', 'commoner.authenticate.views.logout',
        name='logout'),

    url(r'^a/password/change/$',
        'django.contrib.auth.views.password_change',
        name='password_change'),
    url(r'^a/password/change/done/$',
        'django.contrib.auth.views.password_change_done',),
    url(r'^a/password/reset/$',
        'django.contrib.auth.views.password_reset',
        name='password_reset'),
    url(r'^a/password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 
        'django.contrib.auth.views.password_reset_confirm'),
    url(r'^a/password/reset/done/$',
        'django.contrib.auth.views.password_reset_done',),
    url(r'^a/password/reset/complete/$',
        'django.contrib.auth.views.password_reset_complete',),
    url(r'^a/delete/$', 'commoner.profiles.views.delete',
        name='delete_account'),
    url(r'^a/ack/(?P<message_id>\d+)', 
        'commoner.broadcast.views.ack',
        name='ack_message'),
        
    (r'^a/register/complete/$', 
     'django.views.generic.simple.direct_to_template',
     {'template':'registration/success.html'}),
    (r'^a/register/(?P<key>\w+)/', 'commoner.registration.views.complete'),

    # Profile management
    url(r'^p/edit/$', 'commoner.profiles.views.edit_or_create', 
        name='profile_edit'),
    url(r'^p/email/$', 'commoner.profiles.views.change_email', 
        name='change_email'),    

    # Work Registration management
    url(r'^r/add/', 
        'commoner.works.views.add_or_edit',
        name='add_content'),
    url(r'^r/(?P<id>\d+)/edit/', 
        'commoner.works.views.add_or_edit',
        name='edit_content'),
    url(r'^r/(?P<id>\d+)/delete/', 
        'commoner.works.views.delete',
        name='delete_content'),
    url(r'^r/lookup/$', 'commoner.works.views.by_uri',
        name='lookup_work'),
    url(r'^r/(?P<id>\d+)/', 'commoner.works.views.view',
        name='view_work'),
    url(r'^r/all/atom$', 'commoner.works.feeds.user_works_feed',
        name='works_feed'),
    url(r'^r/recent/atom$', 'commoner.works.feeds.recent_updates_feed',
        name='recent_updates_feed'),
    
    # Metadata scraper support
    url(r'^t/triples', 'commoner.scraper.views.triples',
        name='scrape_triples'),

    # Profile badges
    # (r'^i/', include('commoner_i.urls')),

    # OpenID Support
    url(r'^o/xrds/$', 'commoner.server.views.idpXrds', name="server_xrds"),
    (r'^o/trust/$', 'commoner.server.views.trust_decision'),
    (r'^o/endpoint/$', 'commoner.server.views.endpoint'),
    url(r'^o/login/$', 'commoner.server.views.login',
        name='openid_login'),
    url(r'^o/settings/$', 'commoner.server.views.settings',
        name='openid_settings'),
    url(r'^o/trusted/(?P<id>\d+)/delete/', 
        'commoner.server.views.delete_trusted_party',
        name='openid_delete_trusted'),

    url(r'^o/state/$', 'commoner.server.views.state',
        name='openid_state'),

    # Namespace and RDF support
    (r'^n$', 'django.views.generic.simple.direct_to_template',
     {'template':'rdf/ns.html'}),
    (r'^n/rdf$', 'django.views.generic.simple.direct_to_template',
     {'template':'rdf/ns.rdf',
      'mimetype':'application/rdf+xml'}),
    url(r'^r/all/rdf$', 'commoner.profiles.views.all_rdf',
        name='all_rdf'),
        
        
    # Profile views
    url(r'^(?P<username>\w+)/works/$', 'commoner.profiles.views.works',
        name='profile_works'),
    url(r'^(?P<username>\w+)/works/rdf$', 'commoner.profiles.views.user_rdf',
        name='profile_rdf'),
    url(r'^(?P<username>\w+)/works/atom$', 'commoner.works.feeds.user_works_feed',
        name='profile_works_feed'),
    url(r'^(?P<username>\w+)/$', 'commoner.profiles.views.view'),    
    url(r'^(?P<username>\w+)$', 'commoner.profiles.views.view',
            name='profile_view'),
    
    

)

if settings.DEBUG:
    # Profile badges
    urlpatterns += patterns('',
                            (r'^i/', include('commoner_i.urls')),
                            )


if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:], 
         'django.views.static.serve', 
         {'document_root': settings.MEDIA_ROOT}),
        (r'^%s(?P<path>.*)$' % settings.LEGAL_URL[1:], 
         'django.views.static.serve', 
         {'document_root': settings.LEGAL_ROOT}),
    )
