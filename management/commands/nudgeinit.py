import datetime

from django import db
from django.conf import settings
from django.core.management.base import NoArgsCommand

import reversion

"""
nudgeinit
Updated 1/28/2012, Joshua Ruihley

Initializes django-nudge by getting latest versions of all objects in reversion
and marking them as pushed.
"""

class Command(NoArgsCommand):
    
    
    def handle_noargs(self, **options):
        print "Initializing Nudge"