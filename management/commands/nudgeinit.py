import datetime

from django.core.management.base import NoArgsCommand

from reversion.models import Version

from nudge.models import Batch, BatchItem, Setting
from nudge.utils import latest_objects, generate_key

"""
nudgeinit

Initializes django-nudge by getting latest versions of all objects in reversion
and marking them as pushed.
"""

class Command(NoArgsCommand):
    
    def handle_noargs(self, **options):
        """
        clean pushes, get latest of each distinct object and mark as pushed
        """
        
        print "Initializing Nudge"
        print "  - Deleting all batches and batch items"
        Batch.objects.all().delete()
        BatchItem.objects.all().delete()
        
        print "  - Generating initial key"
        settings, created = Setting.objects.get_or_create(pk=1)
        new_key= generate_key()
        settings.local_key=new_key
        settings.save()
        
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