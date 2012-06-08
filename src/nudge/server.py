import binascii, hashlib, json, os, pickle
from django.core import serializers

from Crypto.Cipher import AES

from django.db import models
from django.utils import importlib
from utils import convert_keys_to_string, caster

from nudge.models import Setting

from django.contrib.contenttypes.models import ContentType
from reversion.models import Version

"""
server.py 

commands received from nudge client
"""

    
def valid_batch(batch_info):
    """returns whether a batch format is valid"""
    is_valid = ('id' in batch_info) and ('title' in batch_info) and ('items' in batch_info)
    return is_valid
    
def decrypt(key, ciphertext, iv):
    """decrypts message sent from client using shared symmetric key"""
    ciphertext = binascii.unhexlify(ciphertext)
    decobj = AES.new(key, AES.MODE_CBC, iv)
    plaintext = decobj.decrypt(ciphertext)
    return plaintext
    
def process_batch(key, batch_info, iv):
    """
    loops through items in a batch and processes them
    """
    
    batch_info = pickle.loads(decrypt(key, batch_info, iv.decode('hex')))

    if valid_batch(batch_info):
        items = serializers.deserialize("json", batch_info['items'])
        success = True
        
        for item in items:
            item.save()
            if type(item.object) == Version:
                version=item.object
		if version.type == 2:
                    version.object.delete()
		else:
                    item.object.revert()

    return success
