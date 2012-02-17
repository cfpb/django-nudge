import hashlib, os
from django.db.models.fields.related import ReverseSingleRelatedObjectDescriptor, SingleRelatedObjectDescriptor, ForeignRelatedObjectsDescriptor
from nudge.models import Batch, BatchItem
from reversion.models import Version
from reversion import get_for_object


def related_objects(obj):
	model=type(obj)
	relationship_names= [attr for attr in dir(model) if type(getattr(model,attr)) in  [ReverseSingleRelatedObjectDescriptor, SingleRelatedObjectDescriptor ]]
	return [getattr(obj, relname) for relname in relationship_names if bool(getattr(obj, relname))]


def caster(fields, model):
    relationship_names= [attr for attr in dir(model) if type(getattr(model,attr)) in  [ReverseSingleRelatedObjectDescriptor, SingleRelatedObjectDescriptor, ForeignRelatedObjectsDescriptor]]
    for relationship_name in relationship_names:
        rel=getattr(model, relationship_name)
        if fields.has_key(relationship_name):
        	fields[relationship_name]= rel.field.related.parent_model.objects.get(pk=fields[relationship_name])
		
    return fields



def latest_objects():
    """returns list of lastest versions for each distinct object"""
    distinct_objects = set([version.object for version in Version.objects.all() ])
    deleted_versions=[version for version in Version.objects.all() if version.object == None] 
    
    latest = []
    for o in distinct_objects:
        if not o: continue
        latest_obj=get_for_object(o)[0]
        latest.append(latest_obj)

    return latest + deleted_versions
    
def object_not_pushed(obj):
    """takes a Version object and returns True if object is associated with a batch that has been pushed"""
    batch_items = BatchItem.objects.filter(version=obj).filter(batch__pushed__isnull=False)
    return not batch_items
    
def changed_items():
    """return list of objects that are new or changed and not pushed"""
    latest = latest_objects()
    eligible = []
    for obj in latest:
        if object_not_pushed(obj):
            eligible.append(obj)
    
    return eligible

def add_versions_to_batch(batch, versions):
    """takes a list of Version obects, and adds them to the given Batch"""
    for v in versions:
        item = BatchItem(object_id=v.object_id, version=v, batch=batch)
        item.save()

def collect_eligibles(batch):
    """collects all changed items and adds them to supplied batch"""
    eligibles = changed_items()
    for e in eligibles:
        e.batch = batch
        e.save()
        
def convert_keys_to_string(dictionary):
    """Recursively converts dictionary keys to strings. Found at http://stackoverflow.com/a/7027514/104365 """
    if not isinstance(dictionary, dict):
        return dictionary
    return dict((str(k), convert_keys_to_string(v)) 
        for k, v in dictionary.items())
        
def generate_key():
    """Generate 32 byte key and return hex representation"""
    seed = os.urandom(32)
    key = hashlib.sha256(seed).digest().encode('hex')
    return key 
