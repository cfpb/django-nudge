import datetime, hashlib, json, os, pickle, urllib, urllib2
from urlparse import urljoin

from Crypto.Cipher import AES

from django.core import serializers

from nudge.models import Batch, BatchItem, PushHistoryItem
from nudge.exceptions import *
from utils import related_objects

from django.conf import settings

"""
client.py 

commands to send to nudge server
"""



def encrypt(key, plaintext):
    m = hashlib.md5(os.urandom(16))
    iv = m.digest()
    encobj = AES.new(key, AES.MODE_CBC, iv)
    pad = lambda s: s + (16 - len(s) % 16) * ' '
    return (encobj.encrypt(pad(plaintext)).encode('hex'), iv)

def encrypt_batch(key, b_plaintext):
    """encrypts a pickled batch for sending to server"""
    encrypted, iv= encrypt(key, b_plaintext)
    return { 'batch': encrypted , 'iv':iv.encode('hex') }

def serialize_batch(key, batch):
    """
    returns urlecncoded pickled serialization of a batch ready to be sent to 
    server.
    """
    import pdb;pdb.set_trace()
    batch_items = BatchItem.objects.filter(batch=batch)
    batch_items_serialized = serializers.serialize("json", [batch_item.version for batch_item in batch_items])
    b_plaintext = pickle.dumps({ 'id':batch.id, 'title':batch.title, 'items':batch_items_serialized })
    
    return encrypt_batch(key, b_plaintext)
    




def send_command(target, data):
    """
    sends a nudge api command
    """
    url= urljoin(settings.NUDGE_REMOTE_ADDRESS, target)

    req = urllib2.Request(url, urllib.urlencode(data))

    response = urllib2.urlopen(req)

    return response

def push_batch(batch):
    """
    pushes batch to server, logs push and timestamps on success
    """
    log=PushHistoryItem(batch=batch)
    log.save()
    key = settings.NUDGE_KEY.decode('hex')
    try:
        
        response= send_command('batch/', serialize_batch(key,batch))
        batch.pushed = datetime.datetime.now()
        batch.save()
        log.http_result=response.getcode()
        log.save()
        if log.http_result != 200:
            raise BatchPushFailure(http_status=response.getcode())
    except:
        raise BatchPushFailure
        
def push_test_batch():
    """
    pushes empty batch to server to test settings and returns True on success
    """
    try:
        key = settings.NUDGE_KEY.decode('hex')
        response=send_command('batch/', serialize_batch(key, Batch()))
        return False if response.getcode() != 200 else True
    except:
        return False
