import datetime

from django.core.management.base import NoArgsCommand

from reversion.models import Version
from nudge.utils import generate_key

from nudge.models import Setting

"""
regenerate_key

generates a new local_key
"""

class Command(NoArgsCommand):
    
    def handle_noargs(self, **options):
        settings, created = Setting.objects.get_or_create(pk=1)
        new_key= generate_key()
        settings.local_key=new_key
        settings.save()
        print "new key: ", new_key