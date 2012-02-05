import json, md5, os, pickle, urllib, urllib2

from Crypto.Cipher import AES

from django.core import serializers

from nudge.models import Batch, BatchItem, Setting, PushHistoryItem

"""
client.py 

commands to send to nudge server
"""

SETTINGS = Setting.objects.get(pk=1)

def encrypt_batch(b_plaintext):
    key = SETTINGS.remote_key
    m = md5.new()
    m.update(SETTINGS.remote_address)
    iv = m.digest()
    encobj = AES.new(key, AES.MODE_CBC, iv)
    pad = lambda s: s + (16 - len(s) % 16) * ' '
    return encobj.encrypt(pad(b_plaintext)).encode('hex')

def serialize_batch(batch):
    items = BatchItem.objects.filter(batch=batch)
    versions = []
    for item in items:
        versions.append(item.version)
    batch_items = serializers.serialize("json", versions)
    b_plaintext = pickle.dumps({ 'id':batch.id, 'title':batch.title, 'items':batch_items })
    b_ciphertext = encrypt_batch(b_plaintext)
    return urllib.urlencode({ 'batch': b_ciphertext })
    
def send_command(target, data):
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
