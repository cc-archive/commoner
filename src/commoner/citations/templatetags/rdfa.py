from django import template

from rdflib.Graph import Graph

register = template.Library()

VOCAB_GRAPHS = {}
NAMESPACES = {
    'http://xmlns.com/foaf/0.1/' : 'http://xmlns.com/foaf/0.1/',
    'http://purl.org/dc/terms/' : 'http://purl.org/dc/terms/',
    'http://creativecommons.org/ns#' : 'http://creativecommons.org/schema.rdf',
}
LABELS = {}

def load_vocab_schema(vocab):
    
    g = Graph()
    g.parse(vocab)
    
    VOCAB_GRAPHS[vocab] = g
    LABELS[vocab] = {}
    
    return g
    
def vocab_schema(vocab):
    
    return VOCAB_GRAPHS.get(vocab, load_vocab_schema(vocab))

@register.simple_tag
def rdfslabel(rdf_triple, as_list=True):

    s, p, o = [str(e) for e in rdf_triple]

    schema_uri = filter(lambda x: p.startswith(x), NAMESPACES.keys())

    if len(schema_uri) == 0:
        return u''

    ns = schema_uri[0]
    ns_uri = NAMESPACES[ns]
    if ns not in LABELS.keys():
        LABELS[ns] = {}
    
    #namespace = NAMESPACES[filter(lambda x: rdf_property.startswith(x), NAMESPACES.keys())[0]]
    
    schema = vocab_schema(ns_uri)

    if p not in LABELS[ns].keys():

        q = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?label 
        WHERE { <%s> rdfs:label ?label . }
        """
                
        label_query = q % (p)
        
        results = schema.query(label_query)
        
        if len(results) > 0:
            LABELS[ns][p] = str( list(results)[0][0] )

        else:
            LABELS[ns][p] = p
        
    if as_list:
        return "<li>%s : %s</li>" % ( LABELS.get(ns).get(p), o)
    else:
        return "%s : %s" % ( LABELS.get(ns).get(p).capitalize(), o)
