"""
Commands to send to a nudge server
"""
import datetime
import hashlib
import os
import pickle
import urllib
import urllib2
import json
from Crypto.Cipher import AES

from django.conf import settings
from django.core import serializers
from django.db import models
from django.contrib.contenttypes.models import ContentType

from nudge.models import Batch, BatchPushItem
from itertools import chain
from reversion import get_for_object
from urlparse import urljoin

from .exceptions import CommandException

from django.conf import settings

IGNORE_RELATIONSHIPS = []

if hasattr(settings, 'NUDGE_IGNORE_RELATIONSHIPS'):
    for model_reference in settings.NUDGE_IGNORE_RELATIONSHIPS:
        app_label, model_label = model_reference.split('.')
        ct = ContentType.objects.get_by_natural_key(app_label, model_label)
        IGNORE_RELATIONSHIPS.append(ct.model_class())

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
    batch_objects = []
    dependencies = [] 
    deletions = []

    for batch_item in batch_push_items:
        version = batch_item.version
        if version.type < 2 and version.object:
            updated_obj=version.object
            batch_objects.append(updated_obj)
            options = updated_obj._meta
            fk_fields = [f for f in options.fields if
                         isinstance(f, models.ForeignKey)]
            m2m_fields = [field.name for field in options.many_to_many]
            through_fields = [rel.get_accessor_name() for rel in
                              options.get_all_related_objects()]
            for related_obj in [getattr(updated_obj, f.name) for f in fk_fields]:
                if related_obj and related_obj not in dependencies and type(related_obj) not in IGNORE_RELATIONSHIPS:
                    dependencies.append(related_obj)

            for manager_name in chain(m2m_fields, through_fields):
                manager = getattr(updated_obj, manager_name)
                for related_obj in manager.all():
                    if related_obj and related_obj not in dependencies and type(related_obj) not in IGNORE_RELATIONSHIPS:
                        dependencies.append(related_obj)

        else:
            app_label = batch_item.version.content_type.app_label
            model_label = batch_item.version.content_type.model
            object_id = batch_item.version.object_id
            deletions.append((app_label, model_label, object_id))

    batch_items_serialized = serializers.serialize('json', batch_objects)
    dependencies_serialized = serializers.serialize('json', dependencies)
    b_plaintext = pickle.dumps({'update': batch_items_serialized,
                                'deletions' : json.dumps(deletions),
                                'dependencies': dependencies_serialized})

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
