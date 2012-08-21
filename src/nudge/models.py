from django.db import models
from django.contrib.contenttypes.models import ContentType
from reversion.models import Version

import json

from datetime import date

from exceptions import *
    

class BatchPushItem(models.Model):
    batch=models.ForeignKey(Batch)
    version=models.ForeignKey(Version)
    last_tried=models.DateTimeField(null=True)
    last_attempt_success=models.BooleanField(null=True)


def default_batch_start_date():
    # date last completed batch pushed
    # or date of earliest revision
    # or today

    return date.today()


class Batch(models.Model):
    title = models.CharField(max_length=1000)
    description=models.TextField(blank=True)
    start_date=models.DateField(default=default_batch_start_date)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    preflight = models.DateTimeField(null=True, blank=True)
    first_push_attempt = models.DateTimeField(null=True, blank=True)
    selected_items_packed= models.TextField(default=json.dumps([]))
    
    def __unicode__(self):
        return u'%s' % self.title
    
    def is_valid(self, test_only=True):
         return True
             
                 
    @property
    def selected_items(self):
       if not hasattr(self, '_selected_items'):
           self._selected_items=json.loads(self.selected_items_packed)
       return self._selected_items
        
    
    class Meta:
        verbose_name_plural = "batches"
        permissions = (
        	("push_batch", "Can push batches"),
    	)
        
        
class PushHistoryItem(models.Model):
    batch=models.ForeignKey(Batch, on_delete=models.PROTECT)
    created=models.DateTimeField(auto_now_add=True)
    http_result=models.IntegerField(blank=True, null=True)
    

    
        
      
class BatchItem(models.Model):
    object_id = models.IntegerField()
    version = models.ForeignKey(Version)
    batch = models.ForeignKey(Batch)
    
    def __unicode__(self):
        return u'%s' % self.version.object_repr
