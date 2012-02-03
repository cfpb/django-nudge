import urllib, urllib2
import json

from django.core import serializers

from nudge.models import Batch, BatchItem, Setting, PushHistoryItem

"""
client.py 

commands to send to nudge server
"""
def serialize_batch(batch):
    items = BatchItem.objects.filter(batch=batch)
    versions = []
    for item in items:
        versions.append(item.version)
    batch_items = serializers.serialize("json", versions)
    b = urllib.urlencode({ 'id':batch.id, 'title':batch.title, 'items':batch_items })
    return b
    
def send_command(target, data):
    SETTINGS = Setting.objects.get(pk=1)
    url = "%s/nudge-api/%s/" % (SETTINGS.remote_address, target)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    return response.read()

def push_batch(batch):
    """
    create commands for each item in batch and send them
    """
    log=PushHistoryItem(batch=batch)
    log.save()
    return send_command('batch', serialize_batch(batch))
