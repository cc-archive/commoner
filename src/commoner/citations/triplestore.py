import rdflib
from rdflib import plugin
from rdflib.store import Store, NO_STORE, VALID_STORE
from rdflib.Graph import Graph
from rdflib.Namespace import Namespace
from rdflib.Literal import Literal
from rdflib.URIRef import URIRef

DB_CONFIG = { 
    'host':'localhost',
    'user':'root',
    'password':'doigoid',
    'db':'commoner_citations_rdf',
}
DB_CONFIG_STRING = ','.join(['='.join([k,v]) for k,v in DB_CONFIG.iteritems()])
DEFAULT_STORE_IDENTIFIER = 'webcitations' 

class RdfaStore:
    
    def __init__(self, store_identifier=DEFAULT_STORE_IDENTIFIER):

        self._graphs = {}
        self._status = 0
        self._store = plugin.get('MySQL', Store)(store_identifier)
        self.open() 
        #self._store.config = DB_CONFIG
    
    def open(self):
        """ Open connection to engine """
        return self._store.open(DB_CONFIG_STRING, create=False)
    
    def close(self):
        """ Close the librdf store connection """
        pass

    def create(self):
        """ Create tables for rdf persistence and return a librdf storage
        object """
        
        return self._store.open(DB_CONFIG_STRING, create=True)

    def get_graph(self, graph_uri_identifier):
        """  Returns the conjunctive graph for the provided URI.
        The graph identifiers should be the canonical url for the cited work. """
        return Graph(store=self._store, identifier=URIRef(graph_uri_identifier))

    def namespace(self, base_uri):
        return Namespace(base_uri)
               
    def get_store(self):
        """ Accessor for the RDFStore obj """
        return self._store

