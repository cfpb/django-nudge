"""
(Re)generates a new local_key
"""
from django.core.management.base import NoArgsCommand
from nudge.utils import generate_key


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        new_key = generate_key()
        print "# add this to your settings.py"
        print "NUDGE_KEY = '%s'" % new_key
