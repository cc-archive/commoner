from django.db.models.signals import post_save

from commoner.citations import models
from commoner.snapshots.interface import Snapshot

def queue_snapshot(sender, instance, created, **kwargs):
    
    if created:
        # send a snapshot request to the work queue
        s = Snapshot().render(instance.resolved_url, instance.urlkey)
        
post_save.connect(queue_snapshot, sender=models.Citation)
