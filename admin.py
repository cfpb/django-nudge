from django.contrib import admin
from nudge.models import Batch, BatchItem, Setting
    
admin.site.register(Setting)
admin.site.register(Batch)
admin.site.register(BatchItem)