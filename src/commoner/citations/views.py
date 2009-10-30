import urllib2

from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _

from django.forms.fields import url_re
from commoner.scraper.views import _triples

from models import Citation, MetaData
from forms import AddReuserForm, AddMetadataForm

from triplestore import RdfaStore

from rdfadict import RdfaParser
from rdfadict.sink.graph import GraphSink

import rdflib
from rdflib.Graph import Graph

@login_required
def create(request):

    url = request.GET.get('url') or request.POST.get('url')

    if url is None:
        raise Http404

    # assume that this is an http uri
    if "://" not in url:
        url = u'http://%s' % url
        
    try:
        response = urllib2.urlopen(url)

    except urllib2.URLError, e:

        if hasattr(e, 'reason'):
            message = _("We failed to reach the provided URL, please check the URL and try again.")
        elif hasattr(e, 'code'):
            message = _("The server failed to fulfill our request, please check the URL and try again.")
            
        return render_to_response("citations/error.html",
                                  {'message':message},
                                  context_instance=RequestContext(request))

    # we need to compare fingerprints before saving
    # not diving into the cache stores at this moment so ignore fingerprinting
    c = Citation.objects.create(
        cited_by=request.user,
        cited_url=url,
        resolved_url=response.url)
    
    store = RdfaStore('webcitations').get_store()
    graph_id = rdflib.URIRef(c.canonical_url())

    parser = RdfaParser()
    rdfa_triples = Graph(store=store, identifier=graph_id)
    sink = GraphSink(rdfa_triples)
  
    parser.parse_string(response.read(), c.resolved_url, sink=sink)

    # save our triples in the store
    rdfa_triples.commit()

    # check for license in triples, attributionName, attributionURL, etc.
    q_license = """
    PREFIX cc: <http://creativecommons.org/ns#>
    PREFIX xhtml: <http://www.w3.org/1999/xhtml/vocab#>
    PREFIX dc: <http://purl.org/dc/terms/>
    
    SELECT ?license_uri

        WHERE {
              { <%(uri)s> cc:license ?license_uri . }
          UNION 
              { <%(uri)s> xhtml:license ?license_uri . } 
          UNION
              { <%(uri)s> dc:license ?license_uri . }
        }
    """ 
    citation_license = rdfa_triples.query( q_license % {'uri' : c.resolved_url} )

    if len(citation_license) > 0:
        c.license_url = str( list(citation_license)[0][0] )
        c.save()

    # check for dc:title
    q_title = """
    PREFIX dc: <http://purl.org/dc/terms/>
    SELECT ?title
         WHERE { <%(uri)s> dc:title ?title . }
    """
    citation_title = rdfa_triples.query( q_title % {'uri' : c.resolved_url} )
    if len(citation_title) > 0:
        c.title = str( list(citation_title)[0][0] )
        c.save()

    # if all was successfull, redirect to the new citation's canonical url
    return HttpResponseRedirect(c.get_absolute_url())

def view(request, cid):

    c = get_object_or_404(Citation, urlkey__exact=cid)

    add_reuser_form = AddReuserForm()
    add_metadata_form = AddMetadataForm()
    
    return render_to_response('citations/view.html',
                              {'citation':c,
                               'add_reuser_form': add_reuser_form,
                               'add_metadata_form': add_metadata_form, },
                              context_instance=RequestContext(request))
    
    
def redirect(request, cid):
    c = get_object_or_404(Citation, urlkey__exact=cid)
    return HttpResponseRedirect(c.resolved_url)
