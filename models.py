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
    pushed = models.DateTimeField(null=True, blank=True)
    
    def __unicode__(self):
        return u'%s' % self.title
    
    class Meta:
        verbose_name_plural = "batches"
        
        
class PushHistoryItem(models.Model):
    batch=models.ForeignKey(Batch)
    created=models.DateTimeField(auto_now_add=True)
    http_result=models.IntegerField(blank=True)
    
        
      
class BatchItem(models.Model):
    object_id = models.IntegerField()
    version = models.ForeignKey(Version)
    batch = models.ForeignKey(Batch)
    
    def __unicode__(self):
        return u'%s' % self.version.object_repr