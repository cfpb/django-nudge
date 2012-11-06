import datetime, hashlib, json, os, pickle, urllib, urllib2
from urlparse import urljoin
from itertools import chain
from Crypto.Cipher import AES

from django.core import serializers
from django.db import models
from nudge.models import Batch, BatchPushItem, PushHistoryItem
from nudge.exceptions import *
from utils import related_objects
from reversion import get_for_object
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

def serialize_objects(key, batch_push_items):
    """
    returns urlecncoded pickled serialization of a batch ready to be sent to 
    server.
    """

    batch_versions = [batch_item.version for batch_item in batch_push_items]
    revisions=[]
    related_objects=[]
    for version in batch_versions:
        if version.revision not in revisions:
            revisions.append(version.revision)
        if version.object:
            foreign_key_fields= [f for f in version.object._meta.fields if type(f) == models.fields.related.ForeignKey]
            many_to_many_field_names= [field.name for field in version.object._meta.many_to_many]
            through_field_names=[rel.get_accessor_name() for rel in version.object._meta.get_all_related_objects()]
            for related_object in [getattr(version.object, f.name) for f in foreign_key_fields]:
                if related_object:
                    versions=get_for_object(related_object)
                    if versions and versions[0] not in related_objects:
                        related_objects.append(versions[0])
     
                    else:
                        related_objects.append(related_object)
            for manager_name in chain(many_to_many_field_names, through_field_names):
                manager=getattr(version.object, manager_name)
                for obj in manager.all():
                    if obj not in related_objects:
                        related_objects.append(obj)
    batch_items_serialized = serializers.serialize("json", revisions+related_objects+batch_versions)
    b_plaintext = pickle.dumps({ 'items':batch_items_serialized })
    
    return encrypt_batch(key, b_plaintext)
    




def send_command(target, data):
    """sends a nudge api command"""
    url = urljoin(settings.NUDGE_REMOTE_ADDRESS, target)
    req = urllib2.Request(url, urllib.urlencode(data))
    try:
        return urllib2.urlopen(req)
    except urllib2.HTTPError, e:
        raise CommandException(
          'An exception occurred while contacting %s: %s' %
            (url, e), e)


def push_one(batch_push_item):
    key = settings.NUDGE_KEY.decode('hex')
    if batch_push_item.last_tried and batch_push_item.success:
        return 200
    batch_push_item.last_tried = datetime.datetime.now()
    try:
        response = send_command(
          'batch/', serialize_objects(key, [batch_push_item]))
        if response.getcode() == 200:
            batch_push_item.success=True
    except CommandException, e:
        response = e.orig_exception
    batch_push_item.save()
    return response.getcode()
    

def push_batch(batch):
    """
    pushes batch to server, logs push and timestamps on success
    """

    
    batch_push_items=BatchPushItem.objects.filter(batch=batch)
    if not batch.first_push_attempt:
        batch.first_push_attempt = datetime.datetime.now()
    for batch_push_item in batch_push_items:
        push_one(batch_push_item)
    batch.save()
        
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
