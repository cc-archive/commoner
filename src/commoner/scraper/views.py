import os
import sys
import gc
import rdfadict
import urlparse
import urllib2

from django.http import HttpResponse

import simplejson as json

if sys.version < (2,5):
    # import set support
    from sets import Set as set

FOLLOW_PREDICATES = (
     'http://www.w3.org/1999/02/22-rdf-syntax-ns#seeAlso',
     'http://rdfs.org/sioc/ns#has_owner',
     )

def _load_source(url, subjects=[], sink=None):

    parser = rdfadict.RdfaParser() 

    try:
        # load the specified URL and parse the RDFa
        opener = urllib2.build_opener()
        request = urllib2.Request(url)
        request.add_header('User-Agent',
                 'CC Metadata Scaper http://wiki.creativecommons.org/Metadata_Scraper')
        contents= opener.open(request).read()
        subjects.append(url)

        triples = parser.parse_string(contents, url, sink)

        # look for possible predicates to follow
        for s in triples.keys():
            for p in triples[s].keys():
                if p in FOLLOW_PREDICATES:

                    # for each value of the predicate to follow
                    for o in triples[s][p]:

                        # follow if we haven't already looked here
                        if o not in subjects:
                            _load_source(o, subjects, triples)

    except Exception, e:
        triples = {'_exception': str(e)}

    return triples

def _triples(referer, url):

    # initialize the result
    result = dict(
        source = url,
        referer = referer,
        )

    # parse the RDFa from the document
    triples = _load_source(url)

    ns_cc = 'http://creativecommons.org/ns#'
    ns_wr = 'http://web.resource.org/cc/'

    # mash web.resource assertions to cc.org/ns
    for s in triples.keys():

        if s[:1] == '_': continue

        # walk each predicate, checking if it's in the web.resource ns
        for p in triples[s].keys():

            if p.find(ns_wr) == 0:
                # map this back to cc.org/ns#
                triples[s][ns_cc + p[len(ns_wr):]] = triples[s][p]
                del triples[s][p]

    # add the triples to the result
    result['triples'] = triples
    result['subjects'] = triples.keys()
    gc.collect()

    return result

def triples(request):
    """Extract any triples found in the specified URL and return them
    serialized as JSON."""

    referer = request.META.get('HTTP_REFERER', '')
    return HttpResponse(
        json.dumps(
            _triples(referer, request.GET.get('url', ''))),
        content_type='text/plain')
