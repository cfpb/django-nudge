from django.contrib import admin
from django.contrib.admin.options import *
from django.contrib import messages
from django.forms import ModelForm
from django import forms
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse


from nudge.models import Batch, default_batch_start_date
from nudge.client import push_test_batch

from reversion.admin import VersionAdmin
from reversion.models import Version

from django.http import Http404, HttpResponse, HttpResponseRedirect
from utils import changed_items, add_versions_to_batch, generate_key

import itertools, json

from nudge.exceptions import *


class BatchAdmin(admin.ModelAdmin):
    exclude=['pushed','selected_items_packed']

    
    def render_change_form(self,*args, **kwargs):
        request, context= args[:2]
        batch=context.get('original')
        attached_versions=[]
        if batch:
            attached_versions=[b.version for b in batch.batchitem_set.all()]
            context.update({'versions_selected': attached_versions,
                            'history': batch.pushhistoryitem_set.all(),
                            'editable': not bool(batch.first_push_attempt),
                            'pushing': bool(batch.preflight),
                            'object': batch
            }) 
        else:
            context.update({'editable': True})
        
        if not batch or not batch.pushed:
            if batch:
                available_changes=[item for item in changed_items(batch.start_date, batch=batch) if item not in attached_versions]
            else:
                available_changes=[item for item in changed_items(default_batch_start_date()) if item not in attached_versions]
            
            
            available_changes=itertools.groupby(available_changes, lambda i: i.content_type)            



            context.update({'available_changes':available_changes})
            #import pdb;pdb.set_trace()
        return super(BatchAdmin, self).render_change_form(*args, **kwargs)
        
    def save_model(self, request, obj, form, change):
        
        versions_delete_str=request.POST.getlist('remove_change_from_batch')
        if versions_delete_str:
            versions_to_delete=[Version.objects.get(pk=vid) for vid in [int(vs) for vs in versions_delete_str]]
            for version in versions_to_delete:
                version.batchitem_set.filter(batch=obj).delete()
        
        
        
        items_str=request.POST.getlist('changes_in_batch')
        
        obj.selected_items_packed=json.dumps(items_str)
        obj.save()
            
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
                






admin.site.register(Batch, BatchAdmin)
