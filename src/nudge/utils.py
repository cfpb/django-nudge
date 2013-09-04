import hashlib
import os

from datetime import datetime

from django.db.models.fields.related import (
    ReverseSingleRelatedObjectDescriptor, SingleRelatedObjectDescriptor,
    ForeignRelatedObjectsDescriptor)
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from nudge.models import Batch, BatchPushItem
from nudge.exceptions import CommandException
from reversion.models import Version, Revision, VERSION_TYPE_CHOICES
from reversion import get_for_object

try:
    import simplejson as json
except ImportError:
    import json

VERSION_TYPE_LOOKUP = dict(VERSION_TYPE_CHOICES)


class PotentialBatchItem(object):
    def __init__(self, version, batch=None):
        self.content_type = version.content_type
        self.pk = version.object_id
        self.repr = version.object_repr
        self.version = version
        if batch:
            self.selected = (self.key() in batch.selected_items)

    def __eq__(self, other):
        return (self.content_type == other.content_type and
                self.pk == other.pk)

    def __unicode__(self):
        return self.repr

    def key(self):
        return '~'.join((self.content_type.app_label,
                         self.content_type.model,
                         self.pk))

    def version_type_string(self):
        return VERSION_TYPE_LOOKUP[self.version.type]


def inflate_batch_item(key, batch):
    app_label, model_label, pk = key.split('~')
    content_type = ContentType.objects.get_by_natural_key(app_label,
                                                          model_label)
    latest_version = Version.objects.filter(
        content_type=content_type
    ).filter(
        object_id=pk).order_by('-revision__date_created')[0]
    return BatchPushItem(batch=batch, version=latest_version)


def related_objects(obj):
    model = type(obj)
    relationship_names = []
    related_types = (ReverseSingleRelatedObjectDescriptor,
                     SingleRelatedObjectDescriptor,)
    for attr in dir(model):
        if isinstance(getattr(model, attr), related_types):
            relationship_names.append(attr)
    return [getattr(obj, relname) for relname in relationship_names
            if bool(getattr(obj, relname))]


def caster(fields, model):
    relationship_names = []
    related_types = (ReverseSingleRelatedObjectDescriptor,
                     SingleRelatedObjectDescriptor,
                     ForeignRelatedObjectsDescriptor,)
    for attr in dir(model):
        if isinstance(getattr(model, attr), related_types):
            relationship_names.append(attr)
    for rel_name in relationship_names:
        rel = getattr(model, rel_name)
        if rel_name in fields:
            fields[rel_name] = (rel.field.related.parent_model
                                .objects.get(pk=fields[rel_name]))
    return fields


def changed_items(for_date, batch=None):
    """Returns a list of objects that are new or changed and not pushed"""
    from nudge.client import send_command
    types = []
    for type_key in settings.NUDGE_SELECTIVE:
        app, model = type_key.lower().split('.')
        try:
            types.append(ContentType.objects.get_by_natural_key(app, model))
        except ContentType.DoesNotExist:
            raise ValueError(
                'Model listed in NUDGE_SELECTIVE does not exist: %s.%s' %
                  (app, model))

    eligible_versions = Version.objects.all().filter(
        revision__date_created__gte=for_date,
        content_type__in=types
      ).order_by('-revision__date_created')
    
    pot_batch_items = [PotentialBatchItem(version, batch=batch)
                        for version in eligible_versions]

    seen_pbis = []
    keys = [pbi.key() for pbi in pot_batch_items]
    response = send_command('check-versions/', {
        'keys': json.dumps(keys)}
      ).read()
    try:
        remote_versions = json.loads(response)
    except ValueError, e:
        raise CommandException(
          'Error decoding \'check-versions\' response: %s' % e, e)
   
    def seen(key):
        if key not in seen_pbis:
            seen_pbis.append(key)
            return True
        else:
            return False

    pot_batch_items = filter(seen, pot_batch_items)
    screened_pbis = []
    for pbi in pot_batch_items:
        remote_details = remote_versions[pbi.key()]
        if remote_details:
            version_pk, version_type, timestamp = remote_details
            remote_dt = datetime.strptime(timestamp,'%b %d, %Y, %I:%M %p')
            if remote_dt < pbi.version.revision.date_created.replace(second=0):
                pbi.remote_timestamp = timestamp
                pbi.remote_change_type = VERSION_TYPE_LOOKUP[version_type]
                screened_pbis.append(pbi)
        else:
            screened_pbis.append(pbi)

    return sorted(screened_pbis, key=lambda pbi: pbi.content_type)


def add_versions_to_batch(batch, versions):
    """Takes a list of Version objects, and adds them to the given Batch"""
    for v in versions:
        item = BatchItem(version=v, batch=batch)
        item.save()


def collect_eligibles(batch):
    """Collects all changed items and adds them to supplied batch"""
    for e in changed_items():
        e.batch = batch
        e.save()


def convert_keys_to_string(dictionary):
    """
    Recursively converts dictionary keys to strings.
    Found at http://stackoverflow.com/a/7027514/104365
    """
    if not isinstance(dictionary, dict):
        return dictionary
    return dict([(str(k), convert_keys_to_string(v))
                for k, v in dictionary.items()])


def generate_key():
    """Generate 32 byte key and return hex representation"""
    seed = os.urandom(32)
    key = hashlib.sha256(seed).digest().encode('hex')
    return key
