"""
This module contains functions that aim at making interactions with the
RDF more pleasable by implementing a set of common queries and operations
that would normally take place on the triple store.
"""

def get_license_uri(graph, subject):
    """ Queries the graph for the license that the subject is under.
    Returns a scalar of the first reference to a license that the query
    resolves.  Searches for cc:license, xhtml:license, and dc:license. """

    q = """
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
    results = graph.query( q % {'uri' : subject} )

    try:
        return str(list(results)[0][0])
    except IndexError:
        return ''

def get_work_title(graph, subject):
    """ Query the graph for dc:title or dct:title """
    
    q = """
    PREFIX dc: <http://purl.org/dc/terms/>
    PREFIX dct: <http://purl.org/dc/terms/>
    SELECT ?title
         WHERE {
               { <%(uri)s> dc:title ?title . }
           UNION
               { <%(uri)s> dct:title ?title . }
         }
    """
    results = graph.query( q % {'uri' : subject} )

    try:
        return str(list(results)[0][0])
    except IndexError:
        return ''

def get_attribution_name(graph, subject):
    """ Query the graph for the cc:attributionName of the subject or
    the foaf:name of the dc:creator of the subject """

    q = """
    PREFIX cc: <http://creativecommons.org/ns#>
    PREFIX dc: <http://purl.org/dc/terms/>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>

    SELECT ?name
         WHERE {
               { <%(uri)s> cc:attributionName ?name . }
           UNION
               { <%(uri)s> dc:creator ?creator .
                 ?creator foaf:name ?name . }
         }
    """
    results = graph.query( q % {'uri' : subject} )

    try:
        return str(list(results)[0][0])
    except IndexError:
        return ''

def get_attribution_url(graph, subject):
    """ Return the cc:attributionUrl if it exists """
    q = """
    PREFIX cc: <http://creativecommons.org/ns#>
    SELECT ?url WHERE { <%(uri)s> cc:attributionURL ?url . }
    """
    results = graph.query( q % {'uri' : subject} )
    try:
        return str(list(results)[0][0])
    except IndexError:
        return ''

def get_licensing_metadata(graph, subject):

    q = """
    PREFIX cc: <http://creativecommons.org/ns#>
    PREFIX dc: <http://purl.org/dc/terms/>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX dct: <http://purl.org/dc/terms/>

    SELECT ?license_uri,
           ?title,
           ?attribName,
           ?attribURL,
           ?type,
           ?source,
           ?morePerm

    WHERE {
          { <%(uri)s> cc:license ?license_uri . }
    UNION { <%(uri)s> xhtml:license ?license_uri . }
    UNION { <%(uri)s> dc:license ?license_uri . }
    UNION { <%(uri)s> dc:title ?title . }
    UNION { <%(uri)s> dct:title ?title . }
    UNION { <%(uri)s> cc:attributionName ?name . }
    UNION { <%(uri)s> dc:creator ?creator . ?creator foaf:name ?name . }
    UNION { <%(uri)s> cc:attributionURL ?url . }
    UNION { <%(uri)s> dc:type ?type . }
    UNION { <%(uri)s> dc:source ?source . }
    UNION { <%(uri)s> cc:morePermissions ?morePerm . }

    }
    """

    return graph.query( q % {'uri' : subject} )


CACHED_GRAPHS = {}

def get_namespace_for(property):
    """ Get the URI to the RDF schema that a property is a member of.
    The property can either be an absolute path to the property:

    e.g. 'http://creativecommons.org/ns#attributionName'
    
    or a prefixed version of the vocabulary:

    e.g. 'cc:attributionName'

    The prefixes of the vocabularies will be based around the namespaces
    most regularly seen and how they are most commonly prefixed.
    """

    namespaces = {
        'cc'    : ('http://creativecommons.org/ns#', 'http://creativecommons.org/schema.rdf',),
        'ccnet' : ('http://creativecommons.net/n#', 'http://creativecommons.net/n#',),
        'dc'    : ('http://purl.org/dc/terms/', 'http://purl.org/dc/terms/',),
        'dct'   : ('http://purl.org/dc/terms/', 'http://purl.org/dc/terms/',),
        'foaf'  : ('http://xmlns.com/foaf/0.1/', 'http://xmlns.com/foaf/0.1/',),
        'powder': ('http://www.w3.org/2007/05/powder#',' http://www.w3.org/2007/05/powder#',),
        'rdf'   : ('http://www.w3.org/1999/02/22-rdf-syntax-ns#', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',),
        'sioc'  : ('http://rdfs.org/sioc/ns', 'http://rdfs.org/sioc/ns',),
        'sioc_service': ('http://rdfs.org/sioc/services#', 'http://rdfs.org/sioc/services#',),
        'xhtml' : ('http://www.w3.org/1999/xhtml/vocab#', 'http://www.w3.org/1999/xhtml/vocab#',),
        'xsd'   : ('http://www.w3.org/2001/XMLSchema#', 'http://www.w3.org/2001/XMLSchema#',),
    }
    
    matches = filter(lambda x: property.startswith(x[0]), namespaces.values())
    
    if len(matches) > 0:

        if len(matches) == 1:
            return matches.pop()[1]
        else:
            # return the ns of greatest length (most matching characters)
            return max(matches, key=len)[1]
        
    else:
        # attempt to determine the namespace of a prefixed property
        import re
        prefixed_re = re.compile('([\w]+):([\w])')
        prefixed = re.match(prefixed_re, property)
        
        if prefixed:
            ns = namespaces.get(prefixed.group(1))
            try:
                return ns[1]
            except:
                return None
    raise Exception, "Unidentifiable RDF schema"

def get_rdfs_label(property, namespace=None):
    """ Returns the rdfs:label of an RDF property.  The property can either
    be an absolute reference or the short identifier.  If a property is not an
    absolute URI reference, then the namespace will need to be provided as an
    absolute URI reference.

    If the namespace is not specified, get_namespace_for will be called in an
    attempt to resolve the base URI of the namespace the property belongs to.

    NOTE: prefixed RDF properties are not supported by this function 
    """

    if namespace is None:
        try:
            namespace = get_namespace_for(property)
        except:
            return u''

    if namespace in CACHED_GRAPHS.keys():
        g = CACHED_GRAPHS[namespace]
    else:
        
        from rdflib.Graph import Graph as Graph
        g = Graph()
        g.parse(namespace)
        CACHED_GRAPHS[namespace] = g
    
    q = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?label WHERE { <%s> rdfs:label ?label . }
        """
    
    results = g.query( q % property )
    
    if len(results) > 0:
        return unicode( list(results)[0][0] )
    
    return u''
    
