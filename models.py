from django.db import models
from reversion.models import Version
    
class Setting(models.Model):
    local_address = models.CharField(max_length=255, null=True, blank=True)
    local_key = models.CharField(max_length=255, null=True, blank=True)
    remote_address = models.CharField(max_length=255, null=True, blank=True)
    remote_key = models.CharField(max_length=255, null=True, blank=True)
        
class Batch(models.Model):
    title = models.TextField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "batches"
      
class BatchItem(models.Model):
    object_id = models.IntegerField()
    version = models.ForeignKey(Version)
    batch = models.ForeignKey(Batch)
    push_timestamp = models.DateTimeField(null=True)
    
    def __unicode__(self):
        return self.version.object_repr