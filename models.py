from django.db import models
from reversion.models import Version

from exceptions import *
    
class Setting(models.Model):
    local_address = models.CharField(max_length=255, null=True, blank=True)
    local_key = models.CharField(max_length=255, null=True, blank=True)
    remote_address = models.CharField(max_length=255, null=True, blank=True)
    remote_key = models.CharField(max_length=255, null=True, blank=True)
        
class Batch(models.Model):
    title = models.TextField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    pushed = models.DateTimeField(null=True, blank=True)
    
    def __unicode__(self):
        return u'%s' % self.title
    
    def is_valid(self, test_only=True):
        for batchitem in self.batchitem_set.all():
             valid=True
             other_batches=batchitem.version.batchitem_set.exclude(batch=self)
             if other_batches.count() > 0: 
                 if test_only:
                     valid=False
                 else:
                     raise BatchValidationError
                

             return valid
             
    def delete(self):
    	return False
                 
    
    
    class Meta:
        verbose_name_plural = "batches"
        
    
        
        
class PushHistoryItem(models.Model):
    batch=models.ForeignKey(Batch)
    created=models.DateTimeField(auto_now_add=True)
    http_result=models.IntegerField(blank=True, null=True)
    
        
      
class BatchItem(models.Model):
    object_id = models.IntegerField()
    version = models.ForeignKey(Version)
    batch = models.ForeignKey(Batch)
    
    def __unicode__(self):
        return u'%s' % self.version.object_repr