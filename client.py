import datetime, hashlib, json, os, pickle, urllib, urllib2

from Crypto.Cipher import AES

from django.core import serializers

from nudge.models import Batch, BatchItem, Setting, PushHistoryItem

"""
client.py 

commands to send to nudge server
"""

SETTINGS = Setting.objects.get(pk=1)

def encrypt_batch(b_plaintext):
    """encrypts a pickled batch for sending to server"""
    key = SETTINGS.remote_key.decode('hex')
    m = hashlib.md5(os.urandom(16))
    iv = m.digest()
    encobj = AES.new(key, AES.MODE_CBC, iv)
    pad = lambda s: s + (16 - len(s) % 16) * ' '
    return { 'batch': encobj.encrypt(pad(b_plaintext)).encode('hex'), 'iv':iv.encode('hex') }

def serialize_batch(batch):
    """
    returns urlecncoded pickled serialization of a batch ready to be sent to 
    server.
    """
    items = BatchItem.objects.filter(batch=batch)
    versions = []
    for item in items:
        versions.append(item.version)
    batch_items = serializers.serialize("json", versions)
    b_plaintext = pickle.dumps({ 'id':batch.id, 'title':batch.title, 'items':batch_items })
    return urllib.urlencode(encrypt_batch(b_plaintext))
    
def send_command(target, data):
    """
    sends a nudge api command
    """
    url = "%s/nudge-api/%s/" % (SETTINGS.remote_address, target)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    return response.read()

def push_batch(batch):
    """
    pushes batch to server, logs push and timestamps on success
    """
    log=PushHistoryItem(batch=batch)
    log.save()
    if send_command('batch', serialize_batch(batch)):
        batch.pushed = datetime.datetime.now()
        batch.save()
