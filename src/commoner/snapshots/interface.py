from carrot.messaging import Publisher
from carrot.connection import DjangoBrokerConnection

class Snapshot(Publisher):

    exchange = "snapshot"
    routing_key = "renderer"

    def __init__(self, *args, **kwargs):
        if 'connection' not in kwargs.keys():
            kwargs['connection'] = DjangoBrokerConnection()
        super(Snapshot, self).__init__(*args, **kwargs)

    def render(self, url, identifier=None):
        return self.send({'action':'render',
                          'url':url,
                          'identifier':identifier})
