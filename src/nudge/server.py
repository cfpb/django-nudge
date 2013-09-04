"""
Handles commands received from a Nudge client
"""
import binascii
import pickle
from Crypto.Cipher import AES
from django.contrib.contenttypes.models import ContentType
from django.core import serializers
import reversion
from reversion.models import Version


try:
    import simplejson as json
except ImportError:
    import json




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
    success = True


    if 'dependencies' in batch_info:
        dependencies = serializers.deserialize('json', batch_info['dependencies'])
        for dep in dependencies:
            dep.save()

    if 'update' in batch_info:
        updates = serializers.deserialize('json', batch_info['update'])
        for item in updates:
            with reversion.create_revision():
                item.save()

    if 'deletions' in batch_info:
        deletions = json.loads(batch_info['deletions'])
        for deletion in deletions:
            app_label, model_label, object_id = deletion
            ct = ContentType.objects.get_by_natural_key(app_label, model_label)
            for result in ct.model_class().objects.filter(pk=object_id):
                with reversion.create_revision():
                    result.delete()
                    
    return success
