import binascii, json, os, pickle

from Crypto.Cipher import AES

from django.db import models
from django.utils import importlib
from utils import convert_keys_to_string

from nudge.models import Setting

"""
server.py 

commands received from nudge client
"""

SETTINGS = Setting.objects.get(pk=1)

def get_model(model_str):
    app_name = model_str.split('.')[0]
    model_name = model_str.split('.')[1]
    app = models.get_app(app_name)    
    model_obj = getattr(app, model_name.capitalize())
    return model_obj
    
def valid_batch(batch_info):
    is_valid = ('id' in batch_info) and ('title' in batch_info) and ('items' in batch_info)
    return is_valid
    
def decrypt(key, ciphertext):
    ciphertext = binascii.unhexlify(ciphertext)
    iv = str(SETTINGS.local_address.encode('hex'))[:16]
    decobj = AES.new(key, AES.MODE_CBC, iv)
    plaintext = decobj.decrypt(ciphertext)
    return plaintext
    
def process_item(item):
    if item['fields']['type'] < 2:
        # Add or Update
        item_content = json.loads(item['fields']['serialized_data'])[0]
        model_obj = get_model(item_content['model'])
        id = item_content['pk']
        fields = convert_keys_to_string(item_content['fields'])
        
        new_item = model_obj(pk=id, **fields)
        new_item.save()
        return True
    else:
        # Delete
        return False
    
def process_batch(batch_info):
    key = SETTINGS.local_key
    batch_info = pickle.loads(decrypt(key, batch_info))
    if valid_batch(batch_info):
        items = json.loads(batch_info['items'])
        success = True
        for item in items:
            success = success and process_item(item)
    return success
