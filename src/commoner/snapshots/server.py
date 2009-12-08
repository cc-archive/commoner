from carrot.messaging import Consumer
from carrot.connection import DjangoBrokerConnection

from commoner.snapshots import renderer

from django.conf import settings
import os
import sys

class SnapshotConsumer(Consumer):

    queue = "snapshot"
    exchange = "snapshot"
    routing_key = "renderer"

    def receive(self, message_data, message):

        print "Receiving message: %s" % message
        
        action = message_data['action']
        if action == 'render':
            
            print "received a render action"
            try:

                image = self._action_render(message_data)
                image_stored = self._action_store(image, message_data)

                if image_stored:
                    # signal to commoner.citations that things succeeded :)
                    message.ack()
                else:
                    pass
                
            except renderer.TimeoutError, te:
                # need to track this...
                # this returns unsupported message errors???
                message.reject()
                return 
                
            except (renderer.InvalidURLError, renderer.LoadingError), err:
                # need to diagnose issue
                # not support either???
                print err
                message.reject()
                return
                
            except Exception, e:                
                raise Exception("Malformed message_data for render action: %s" % e)
            
        else:
            raise Exception("Unkown action: %s" % action)
        
    def _action_render(self, message_data):

        if 'url' not in message_data.keys():
            raise Exception("The URL to render was not specified.")
        
        r = renderer.WebkitRenderer()

        try:
            image = r.render(message_data['url'])
            return image
        except RuntimeError, r:
            # if error was remote, raise notification to caller to signal a requeue 
            raise r
        
        # reduce Qt footprint garbage
        del r
        
    def _action_store(self, image, message_data):
        
        if 'identifier' not in message_data.keys():
            raise Exception("An identifier must be provided to output a rendering.")

        filename = os.path.join(settings.MEDIA_ROOT, settings.SNAPSHOT_STORAGE,
                                "%s.png" % message_data['identifier'])

        print "Saving image %s" % filename

        image.save( filename, 'png')
        
        return True
        
def main():
   
    print "Snapshot queue consumer listening..."

    conn = DjangoBrokerConnection()

    # instantiate a consumer object   
    consumer = SnapshotConsumer(connection=conn)
    consumer.wait()

