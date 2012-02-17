from django.contrib import admin
from django.contrib.admin.options import *
from django.contrib import messages
from django.forms import ModelForm
from django import forms
from django.utils.translation import ugettext as _


from nudge.models import Batch, BatchItem, Setting
from nudge.client import push_test_batch

from reversion.admin import VersionAdmin
from reversion.models import Version

from django.http import Http404, HttpResponse, HttpResponseRedirect
from utils import changed_items, add_versions_to_batch, generate_key


from nudge.exceptions import *


class NudgeAdmin(VersionAdmin):
    pass

    

class SettingsAdmin(admin.ModelAdmin):

    readonly_fields=['local_key']
    def render_change_form(self,*args, **kwargs):
         
         
         return super(SettingsAdmin, self).render_change_form(*args, **kwargs)
         
    def changelist_view(self,*args, **kwargs):
        SETTINGS, created = Setting.objects.get_or_create(pk=1)
        return HttpResponseRedirect(args[0].environ['PATH_INFO']+str(SETTINGS.id))
        
    def add_view(self,*args, **kwargs):
        SETTINGS, created = Setting.objects.get_or_create(pk=1)
        return HttpResponseRedirect(args[0].environ['PATH_INFO']+"../"+str(SETTINGS.id))
        
    def change_view(self, request, *args, **kwargs):
        return super(SettingsAdmin, self).change_view(request, *args, **kwargs)
        
        
    def response_change(self,request,object):
        msg = _('The local key was re-generated successfully.')
        if "_regen_key" in request.POST:
            
            object.local_key = generate_key()
            object.save()
            self.message_user(request, msg)
            if "_popup" in request.REQUEST:
                return HttpResponseRedirect(request.path + "?_popup=1")
            else:
                return HttpResponseRedirect(request.path)
        elif '_test' in request.POST:
            if push_test_batch():
                messages.info(request, "It works! Communication with remote server was successful.")
            else:
                messages.error(request, "Pushing a test batch failed-- please see a system administrator")
        return super(SettingsAdmin, self).response_change(request,object)


    def save_model(self, request, obj, form, change):
        obj.save()

            

class BatchAdmin(admin.ModelAdmin):
    

    
    def render_change_form(self,*args, **kwargs):
        request, context= args[:2]
        batch=context.get('original')
        attached_versions=[]
        if batch:
            attached_versions=[b.version for b in batch.batchitem_set.all()]
            context.update({'versions_selected': attached_versions,
                            'history': batch.pushhistoryitem_set.all(),
                            'editable': not bool(batch.pushed),
                            'object': batch
            }) 
        else:
            context.update({'editable': True})
            
            
        
        if not batch or not batch.pushed:
            available_changes=[item for item in changed_items() if item not in attached_versions]
            context.update({'available_changes':available_changes})
        return super(BatchAdmin, self).render_change_form(*args, **kwargs)
        
    def save_model(self, request, obj, form, change):
        obj.save()
        versions_delete_str=request.POST.getlist('remove_change_from_batch')
        if versions_delete_str:
            versions_to_delete=[Version.objects.get(pk=vid) for vid in [int(vs) for vs in versions_delete_str]]
            for version in versions_to_delete:
                version.batchitem_set.filter(batch=obj).delete()
        
        
        
        versions_str=request.POST.getlist('changes_in_batch')
        if versions_str:
            versions=[Version.objects.get(pk=vid) for vid in [int(vs) for vs in versions_str]]
            add_versions_to_batch(obj, versions)
            
            
        if request.POST.get(u'_save_and_push'):
            from client import push_batch
            if obj.is_valid():
                obj.save()
                try:
                    push_batch(obj)
                    messages.info(request, "Batch was pushed successfully")
                except BatchPushFailure as exc:
                    messages.error(request, "Pushing this batch failed (%s), please notify a system administrator" % exc.http_status)
            else:
                messages.error(request, "This batch is invalid (perhaps there are items that are already in other batches?)")
                





admin.site.register(Setting, SettingsAdmin)
admin.site.register(Batch, BatchAdmin)
