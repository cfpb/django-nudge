import datetime

from django import db
from django.conf import settings
from django.db.models import Max
from django.core.management.base import NoArgsCommand

from nudge.models import Batch, BatchItem
from reversion.models import Version

"""
nudgeinit
Updated 1/28/2012, Joshua Ruihley

Initializes django-nudge by getting latest versions of all objects in reversion
and marking them as pushed.
"""

class Command(NoArgsCommand):
    
    def handle_noargs(self, **options):

        def latest_objects():
            """
            returns list of lastest versions for each distinct object
            """
             
            distinct_objects = Version.objects.values('object_id_int').distinct()
            latest = []
            for o in distinct_objects:
                latest_obj = Version.objects.filter(object_id_int=o['object_id_int']).order_by('-revision__date_created')[:1]
                latest.append(latest_obj[0])

            return latest
                
        """
        clean pushes, get latest of each distinct object and mark as pushed
        """
        
        print "Initializing Nudge"
        print "  - Deleting all batches and batch items"
        Batch.objects.all().delete()
        BatchItem.objects.all().delete()
        
        print "  - Creating silent batch"
        silent = Batch(title="Nudge Initialization")
        silent.save()
        
        print "  - Adding objects to batch"
        latest = latest_objects()
        for l in latest:
            batch_item = BatchItem(object_id=l.object_id, version=l, batch=silent)
            batch_item.save()
            
        print "  - Marking batch as pushed"
        silent.pushed = datetime.datetime.now()
        silent.save()