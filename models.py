from django.db import models
    
class Setting(models.Model):
    local_address = models.CharField(max_length=255, null=True, blank=True)
    local_key = models.CharField(max_length=255, null=True, blank=True)
    remote_address = models.CharField(max_length=255, null=True, blank=True)
    remote_key = models.CharField(max_length=255, null=True, blank=True)