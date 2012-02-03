import json

from django.db import models
from django.utils import importlib
from utils import convert_keys_to_string


def get_model(model_str):
    app_name = model_str.split('.')[0]
    model_name = model_str.split('.')[1]
    app = models.get_app(app_name)    
    model_obj = getattr(app, model_name.capitalize())
    return model_obj
    
def valid_batch(batch_info):
    is_valid = ('id' in batch_info) and ('title' in batch_info) and ('items' in batch_info)
    return is_valid
    
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
    if valid_batch(batch_info):
        items = json.loads(batch_info['items'])
        success = True
        for item in items:
            success = success and process_item(item)
        
    return success