import urllib2

from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

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
