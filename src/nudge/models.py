from django.db import models
from reversion.models import Version

from exceptions import *
    
class Setting(models.Model):
    local_key = models.CharField("Secret",max_length=255, null=True, blank=True, help_text="This is the key your client will need to push changes to this server.")
    remote_address = models.CharField("Server to push changes to", max_length=255, null=True, blank=True, help_text="This will be blank on your production server")
    remote_key = models.CharField(max_length=255, null=True, blank=True, help_text="This is the 'secret' displayed in the Nudge settings displayed on your production server")
        
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
                     raise BatchValidationError(self)
                

             return valid
             
                 
    
    
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