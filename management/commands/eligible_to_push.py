import datetime

from django.core.management.base import NoArgsCommand

from reversion.models import Version

from nudge.models import Batch, BatchItem
from nudge.utils import latest_objects, object_not_pushed, changed_items

"""
nudgeinit

Initializes django-nudge by getting latest versions of all objects in reversion
and marking them as pushed.
"""

class Command(NoArgsCommand):
    
    def handle_noargs(self, **options):
        """
        return list of objects that are new or changed and not pushed
        """
        
        print changed_items()