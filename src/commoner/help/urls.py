from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

urlpatterns = patterns(
    '',
    
    # Help pages
    (r'^about/$', 'django.views.generic.simple.direct_to_template',
	 {'template':'help/about.html'}),
    (r'^openid/$', 'django.views.generic.simple.direct_to_template',
	 {'template':'help/openid.html'}),
    (r'^privacy/$', 'django.views.generic.simple.redirect_to',
     {'url':'http://creativecommons.org/privacy', 
      'permanent':True}),
    (r'^policies/privacy/20081001/', 
     'django.views.generic.simple.direct_to_template',
     {'template':'help/privacy-20081001.html'}),
    url(r'^contact/$', 'commoner.help.views.contact',
        name='contact_form'),
    (r'^contact/thanks/$', 'django.views.generic.simple.direct_to_template',
	 {'template':'help/contact_thanks.html'}),
    url(r'^metrics/$', 'commoner.metrics.views.stats', name='metrics'),    

)
