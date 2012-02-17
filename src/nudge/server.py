import binascii, hashlib, json, os, pickle
from django.core import serializers

from Crypto.Cipher import AES

from django.db import models
from django.utils import importlib
from utils import convert_keys_to_string, caster

from nudge.models import Setting

from django.contrib.contenttypes.models import ContentType

"""
server.py 

commands received from nudge client
"""



def get_model(model_str):
    """returns model object based on string provided by batch item"""
    app_name = model_str.split('.')[0]
    model_name = model_str.split('.')[1]
    return ContentType.objects.get_by_natural_key(app_name, model_name).model_class()
    
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
    
def process_item(item):
    """
    examines an item in a batch, determines if it should be added, updated or
    deleted and performs the command
    """
    
    item_content = json.loads(item['fields']['serialized_data'])[0]
    model_obj = get_model(item_content['model'])
    id = item_content['pk']
    fields = convert_keys_to_string(item_content['fields'])
    
    if item['fields']['type'] < 2:
        # Add or Update
        fields=caster(fields, model_obj)
        new_item = model_obj(pk=id, **fields)
        new_item.save()
        return True
    else:
        # Delete
        del_item = model_obj.objects.get(pk=id)
        del_item.delete()
        return True
    
def process_batch(key, batch_info, iv):
    """
    loops through items in a batch and processes them
    """
    batch_info = pickle.loads(decrypt(key, batch_info, iv.decode('hex')))
    if valid_batch(batch_info):
        items = json.loads(batch_info['items'])
        success = True
        for item in items:
            success = success and process_item(item)
    return success
