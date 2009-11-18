import urllib2

from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _

from django.forms.fields import url_re
from commoner.scraper.views import _triples

from models import Citation, MetaData
from forms import AddCitationForm, AddReuserForm, AddMetadataForm

from rdf.store import RdfaStore
from rdf import helper

from rdfadict import RdfaParser
from rdfadict.sink.graph import GraphSink

import rdflib
from rdflib.Graph import Graph

@login_required
def create(request):

    url = request.GET.get('url') or request.POST.get('url')
    
    if url is None:
        form = AddCitationForm()
        return render_to_response("citations/create.html",
                                  {'form':form},
                                  context_instance=RequestContext(request))
    else:
        form = AddCitationForm({'url':url})
        
    if not form.is_valid():
        return render_to_response("citations/create.html",
                                  {'form':form},
                                  context_instance=RequestContext(request))
    
    # creating now so that a permalink for the citation is generated
    c = Citation.objects.create(
        cited_by=request.user,
        cited_url=url,
        resolved_url=form.response.url)

    
    store = RdfaStore('webcitations').get_store()
    # the graph's identifier is the newly generated permalink for this citation
    graph_id = rdflib.URIRef(c.canonical_url())
    # use the parser to scrape and store the RDFa embedded at this URL
    parser = RdfaParser()
    # initialize and empty graph to dump the cited work's triples into
    rdfa_triples = Graph(store=store, identifier=graph_id)
    sink = GraphSink(rdfa_triples)
    # use rdfadict to parse the data at this url and populate the sink with the
    # resulting triples 
    parser.parse_string(form.response.read(), form.response.url, sink=sink)
    # save this graph to the RDF store db
    rdfa_triples.commit()

    # before finishing, look for any license information to save in
    license_url = helper.get_license_uri(rdfa_triples, c.resolved_url) 
    # query for the title of the work being cited
    title = helper.get_work_title(rdfa_triples, c.resolved_url)
    # save these fields to the citation
    if title or license_url:
        c.title = title
        c.license_url = license_url
        c.save()

    # loop through triples of the graph and for any that the rdfs:label can
    # be determined, add the data as a MetaData object for this citation
    # NOTE: this bit will dramatically slow the runtime, 
    for s,p,o in rdfa_triples:
        label = helper.get_rdfs_label(p)
        if label != u'':
            # Store label information in a MetaData object
            m = MetaData.objects.create(citation=c, key=label, value=unicode(o))
    
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
