"""
Handles commands received from a Nudge client
"""
import binascii
import pickle
from Crypto.Cipher import AES
from django.contrib.contenttypes.models import ContentType
from reversion.models import Version, VERSION_DELETE

try:
    import simplejson as json
except ImportError:
    import json


def valid_batch(batch_info):
    """Returns whether a batch format is valid"""
    return 'items' in batch_info


def decrypt(key, ciphertext, iv):
    """Decrypts message sent from client using shared symmetric key"""
    ciphertext = binascii.unhexlify(ciphertext)
    decobj = AES.new(key, AES.MODE_CBC, iv)
    plaintext = decobj.decrypt(ciphertext)
    return plaintext


def versions(keys):
    results = {}
    for key in keys:
        app, model, pk = key.split('~')
        content_type = ContentType.objects.get_by_natural_key(app, model)
        versions = Version.objects.all().filter(
            content_type=content_type
        ).filter(object_id=pk).order_by('-revision__date_created')
        if versions:
            latest = versions[0]
            results[key] = (latest.pk,
                            latest.type,
                            latest.revision
                            .date_created.strftime('%b %d, %Y, %I:%M %p'))
        else:
            results[key] = None
    return json.dumps(results)


def process_batch(key, batch_info, iv):
    """Loops through items in a batch and processes them."""
    batch_info = pickle.loads(decrypt(key, batch_info, iv.decode('hex')))
    if valid_batch(batch_info):
        items = serializers.deserialize('json', batch_info['items'])
        success = True
        for item in items:
            item.save()
            if isinstance(Version, item.object):
                version = item.object
                if version.type == VERSION_DELETE:
                    if version.object:
                        version.object.delete()
                else:
                    item.object.revert()
    return success
