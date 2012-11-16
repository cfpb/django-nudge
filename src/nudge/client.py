"""
Commands to send to a nudge server
"""
import datetime
import hashlib
import os
import pickle
import urllib
import urllib2
from Crypto.Cipher import AES
from django.conf import settings
from django.core import serializers
from django.db import models
from nudge.models import Batch, BatchPushItem
from itertools import chain
from reversion import get_for_object
from urlparse import urljoin


def encrypt(key, plaintext):
    m = hashlib.md5(os.urandom(16))
    iv = m.digest()
    encobj = AES.new(key, AES.MODE_CBC, iv)
    pad = lambda s: s + (16 - len(s) % 16) * ' '
    return (encobj.encrypt(pad(plaintext)).encode('hex'), iv)


def encrypt_batch(key, b_plaintext):
    """Encrypts a pickled batch for sending to server"""
    encrypted, iv = encrypt(key, b_plaintext)
    return {'batch': encrypted, 'iv': iv.encode('hex')}


def serialize_objects(key, batch_push_items):
    """
    Returns an urlencoded pickled serialization of a batch ready to be sent
    to a nudge server.
    """
    batch_versions = [batch_item.version for batch_item in batch_push_items]
    revisions = []
    related_objects = []
    for version in batch_versions:
        if version.revision not in revisions:
            revisions.append(version.revision)
        if version.object:
            options = version.object._meta
            fk_fields = [f for f in options.fields if
                         isinstance(f, models.ForeignKey)]
            m2m_fields = [field.name for field in options.many_to_many]
            through_fields = [rel.get_accessor_name() for rel in
                              options.get_all_related_objects()]
            for rel in [getattr(version.object, f.name) for f in fk_fields]:
                if rel:
                    versions = get_for_object(rel)
                    if versions and versions[0] not in related_objects:
                        related_objects.append(versions[0])
                    else:
                        related_objects.append(rel)
            for manager_name in chain(m2m_fields, through_fields):
                manager = getattr(version.object, manager_name)
                for obj in manager.all():
                    if obj not in related_objects:
                        related_objects.append(obj)
    batch_items_serialized = serializers.serialize('json', (revisions +
                                                            related_objects +
                                                            batch_versions))
    b_plaintext = pickle.dumps({'items': batch_items_serialized})
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
    Pushes a batch to a server, logs push and timestamps on success
    """
    batch_push_items = BatchPushItem.objects.filter(batch=batch)
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
        response = send_command('batch/', serialize_batch(key, Batch()))
        return False if response.getcode() != 200 else True
    except:
        return False
