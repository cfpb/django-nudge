import datetime

from django.core.management.base import NoArgsCommand

from reversion.models import Version

from nudge.client import send_command
from nudge.models import Batch, BatchItem
from nudge.utils import latest_objects, object_not_pushed, changed_items

class Command(NoArgsCommand):
    
    def handle_noargs(self, **options):
        """
        adds all eligible items to a batch
        """
        
        print "Creating a new batch with all eligible items"
        
        print " - creating new batch"
        new_batch = Batch(title='All Eligible Items')
        new_batch.save()
        
        print " - adding items to batch"
        eligible = changed_items()
        for e in eligible:
            item = BatchItem(object_id=e.object_id, version=e, batch=new_batch)
            item.save()
            print "   - Added %s" % e