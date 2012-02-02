import urllib, urllib2
import json

from django.core import serializers

from nudge.models import Batch, BatchItem, Setting

"""
client.py 

commands to send to nudge server
"""

SETTINGS = Setting.objects.get(pk=1)

def serialize_batch(batch):
    batch_items = serializers.serialize("json", BatchItem.objects.filter(batch=batch))
    b = urllib.urlencode({ 'id':batch.id, 'title':batch.title, 'items':batch_items })
    print b
    return b
    
def send_command(target, data):
    url = "%s/nudge-api/%s/" % (SETTINGS.remote_address, target)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    return response.read()

def push_batch(batch):
    """
    create commands for each item in batch and send them
    """
    return send_command('batch', serialize_batch(batch))