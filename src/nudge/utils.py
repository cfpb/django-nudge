import hashlib, os
from django.db.models.fields.related import ReverseSingleRelatedObjectDescriptor, SingleRelatedObjectDescriptor, ForeignRelatedObjectsDescriptor
from django.contrib.contenttypes.models import ContentType
from nudge.models import Batch, BatchPushItem, version_type_map
from reversion.models import Version, Revision
from reversion import get_for_object

from django.conf import settings



class PotentialBatchItem(object):
	def __init__(self, version, batch=None):
            self.content_type=version.content_type
            self.pk=version.object_id
            self.repr= version.object_repr
            self.version=version
            if batch:
                self.selected=self.key() in batch.selected_items

	
        def __eq__(self, other):
            return (self.content_type==other.content_type and self.pk==other.pk)

        def __unicode__(self):
            return self.repr

        def key(self):
            return '~'.join([self.content_type.app_label,self.content_type.model, self.pk])

        def version_type_string(self):
            return version_type_map[self.version.type]


def inflate_batch_item(key, batch):
    app_label, model_label, pk= key.split('~')
    content_type=ContentType.objects.get_by_natural_key(app_label, model_label)
    latest_version=Version.objects.filter(content_type=content_type).filter(object_id=pk).order_by('-revision__date_created')[0]

    
    return BatchPushItem(batch=batch, version=latest_version)

   
        


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



    
def changed_items(for_date, batch=None):
    """return list of objects that are new or changed and not pushed"""
    types=[]
    for type_key in settings.NUDGE_SELECTIVE:
       app, model = type_key.split('.')
       types.append(ContentType.objects.get_by_natural_key(app,model))
    


    eligible_versions=Version.objects.all().filter(revision__date_created__gte=for_date).filter(content_type__in=types).order_by('-revision__date_created').distinct(['content_type_id','object_id'])
    
    pot_batch_items=[PotentialBatchItem(version, batch=batch) for version in eligible_versions]
 
    seen_pbis=[]

    def seen(key):
        if key not in seen_pbis:
            seen_pbis.append(key)
            return True
        else:
            return False

    
    pot_batch_items=filter(seen,pot_batch_items)
    return set(pot_batch_items)

def add_versions_to_batch(batch, versions):
    """takes a list of Version obects, and adds them to the given Batch"""
    for v in versions:
        item = BatchItem(version=v, batch=batch)
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
