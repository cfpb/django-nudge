from nudge.models import Batch, BatchItem
from reversion.models import Version

def latest_objects():
    """
    returns list of lastest versions for each distinct object
    """
     
    distinct_objects = Version.objects.values('object_id_int').distinct()
    latest = []
    for o in distinct_objects:
        latest_obj = Version.objects.filter(object_id_int=o['object_id_int']).order_by('-revision__date_created')[:1]
        latest.append(latest_obj[0])

    return latest
    
def object_not_pushed(obj):
    """
    takes a Version object and returns True if object is associated with a batch that has been pushed
    """
    batch_items = BatchItem.objects.filter(version=obj).filter(batch__pushed__isnull=False)
    return not batch_items
    
def changed_items():
    """
    return list of objects that are new or changed and not pushed
    """
    
    latest = latest_objects()
    eligible = []
    for obj in latest:
        if object_not_pushed(obj):
            eligible.append(obj)
    
    return eligible

def add_versions_to_batch(batch, versions):
    """
    takes a list of Version obects, and adds them to the given Batch
    """
    for v in versions:
        item = BatchItem(object_id=v.object_id, version=v, batch=batch)
        item.save()

    
    
    

def collect_eligibles(batch):
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