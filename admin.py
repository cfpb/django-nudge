from django.contrib import admin
from nudge.models import Batch, BatchItem, Setting

from reversion.admin import VersionAdmin
from reversion.models import Version

from django.http import Http404, HttpResponse, HttpResponseRedirect
from utils import changed_items, add_versions_to_batch


class NudgeAdmin(VersionAdmin):
    pass

    


class BatchAdmin(admin.ModelAdmin):
    
    
    def render_change_form(self,*args, **kwargs):
        request, context= args[:2]
        batch=context.get('original')
        attached_versions=[]
        if batch:
            attached_versions=[b.version for b in batch.batchitem_set.all()]
            context.update({'versions_selected': attached_versions})
        
        
        if not batch or not batch.pushed:
            available_changes=[item for item in changed_items() if item not in attached_versions]
            context.update({'available_changes':available_changes})
            
        return super(BatchAdmin, self).render_change_form(*args, **kwargs)
        
    def save_model(self, request, obj, form, change):
        obj.save()
        versions_delete_str=request.POST.get('remove_change_from_batch')
        if versions_delete_str:
            versions_to_delete=[Version.objects.get(pk=vid) for vid in [int(vs) for vs in versions_delete_str]]
            for version in versions_to_delete:
                version.batchitem_set.filter(batch=obj).delete()
        
        
        
        versions_str=request.POST.get('changes_in_batch')
        if versions_str:
            versions=[Version.objects.get(pk=vid) for vid in [int(vs) for vs in versions_str]]
            add_versions_to_batch(obj, versions)
            
            
            
        #import pdb;pdb.set_trace() 




admin.site.register(Setting)
admin.site.register(Batch, BatchAdmin)
admin.site.register(BatchItem)