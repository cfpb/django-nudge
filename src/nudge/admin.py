from django.contrib import admin
from django.contrib.admin.options import *
from django.contrib import messages
from django.forms import ModelForm
from django import forms
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType
from django.http import Http404, HttpResponse, HttpResponseRedirect

from django.db import models, transaction, router
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator

from django.template.response import SimpleTemplateResponse, TemplateResponse
from django.conf.urls.defaults import *
from django.shortcuts import render_to_response, redirect
from django.utils.safestring import mark_safe

from nudge.models import Batch, BatchPushItem, default_batch_start_date
from nudge.client import push_batch, push_one

from reversion.admin import VersionAdmin
from reversion.models import Version

from django.http import Http404, HttpResponse, HttpResponseRedirect
from utils import changed_items, add_versions_to_batch, generate_key, inflate_batch_item

import itertools, json

from nudge.exceptions import *
from datetime import datetime

class BatchAdmin(admin.ModelAdmin):
    exclude=['preflight','selected_items_packed', 'first_push_attempt']



    def render_change_form(self,*args, **kwargs):
        request, context= args[:2]
        batch=context.get('original')
        attached_versions=[]
        if batch:

            context.update({'pushing': bool(batch.preflight),
                            'object': batch,
            }) 
        else:
            context.update({'editable': True})
        

        if batch:
            available_changes=[item for item in changed_items(batch.start_date, batch=batch) if item not in attached_versions]
        else:
            available_changes=[item for item in changed_items(default_batch_start_date()) if item not in attached_versions]
            

        context.update({'available_changes':available_changes})

        return super(BatchAdmin, self).render_change_form(*args, **kwargs)
    

 


    def change_view(self, request, object_id, extra_context=None):
        model = self.model
        opts = model._meta

        obj = self.get_object(request, unquote(object_id))


        if obj.preflight:
            return HttpResponseRedirect('push/')
        if u'_save_and_push' not in request.POST:
           
            return super(BatchAdmin, self).change_view(request, object_id, extra_context=extra_context)
        else:


            ModelForm = self.get_form(request, obj)
            formsets = []
            form = ModelForm(request.POST, request.FILES, instance=obj)
            if form.is_valid():
                form_validated = True
                new_object = self.save_form(request, form, change=True)
            else:
                form_validated = False
                new_object = obj
            prefixes = {}
            for FormSet, inline in zip(self.get_formsets(request, new_object),
                                       self.inline_instances):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
                if prefixes[prefix] != 1:
                    prefix = "%s-%s" % (prefix, prefixes[prefix])
                formset = FormSet(request.POST, request.FILES,
                                  instance=new_object, prefix=prefix,
                                  queryset=inline.queryset(request))

                formsets.append(formset)

            if all_valid(formsets) and form_validated:
                self.save_model(request, new_object, form, change=True)
                form.save_m2m()
                for formset in formsets:
                    self.save_formset(request, form, formset, change=True)

                change_message = self.construct_change_message(request, form, formsets)
                self.log_change(request, new_object, change_message)


                return HttpResponseRedirect('push/')


        return self.render_change_form(request, context, change=True, obj=obj)




    @csrf_protect_m
    @transaction.commit_on_success
    def pushing_view(self, request, object_id, form_url='', extra_context=None):

        if request.is_ajax() and u'push-batch-item' in request.POST:
            batch_push_item=BatchPushItem.objects.get(pk=request.POST[u'push-batch-item'])
            push_one(batch_push_item)
            return render_to_response('admin/nudge/batch/_batch_item_row.html', {'batch_item': batch_push_item})
            

        batch=self.model.objects.get(pk=object_id)
        
        if request.method == 'POST' and u'abort_preflight' in request.POST:
            BatchPushItem.objects.filter(batch=batch).delete()
            batch.preflight=None
            batch.save()

        if request.method == 'POST' and u'push_now' in request.POST:
            push_batch(batch)


        if not batch.preflight:
            return HttpResponseRedirect('../')
        
        batch_push_items= BatchPushItem.objects.filter(batch=batch)  
        context={'batch_push_items':batch_push_items, 'media': mark_safe(self.media)}
        
        opts = self.model._meta
        app_label = opts.app_label
        return TemplateResponse(request, [
            "admin/%s/%s/push.html" % (app_label, opts.object_name.lower()),
        ], context, current_app=self.admin_site.name)
    

    def get_urls(self):
        urlpatterns=super(BatchAdmin, self).get_urls()



        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.module_name


        urlpatterns = patterns('', url(r'^(.+)/push/$',
                wrap(self.pushing_view),
                name='%s_%s_push' % info)) + urlpatterns
        return urlpatterns
   
    def save_model(self, request, obj, form, change):
        
        items_str=request.POST.getlist('changes_in_batch')
        
        obj.selected_items_packed=json.dumps(items_str)
        if u'_save_and_push' in request.POST:
            obj.preflight=datetime.now()
            obj.save()
            for selected_item in obj.selected_items:
                bi=inflate_batch_item(selected_item, obj)
                bi.save()
            request.POST['_continue']=1
        obj.save()
            







admin.site.register(Batch, BatchAdmin)
