from datetime import datetime
from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from django.contrib.admin.util import unquote
from django.contrib.auth.admin import csrf_protect_m
from django.db import transaction
from django.forms.formsets import all_valid
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.response import TemplateResponse
from django.utils.functional import update_wrapper
from django.utils.safestring import mark_safe
from nudge import client
from nudge import utils
from nudge.models import Batch, BatchPushItem, default_batch_start_date

try:
    import simplejson as json
except ImportError:
    import json


class BatchAdmin(admin.ModelAdmin):
    exclude = ['preflight', 'selected_items_packed', 'first_push_attempt']

    def render_change_form(self, *args, **kwargs):
        request, context = args[:2]
        batch = context.get('original')
        attached_versions = []
        if batch:
            context.update({
                'pushing': bool(batch.preflight),
                'object': batch,
            })
        else:
            context.update({'editable': True})

        if batch:
            available_changes = [item for item in utils.changed_items(
                batch.start_date, batch=batch)
                if item not in attached_versions]
        else:
            available_changes = [item for item in utils.changed_items(
                default_batch_start_date()) if item not in attached_versions]

        context.update({'available_changes': available_changes})

        return super(BatchAdmin, self).render_change_form(*args, **kwargs)

    def change_view(self, request, object_id, extra_context=None):
        obj = self.get_object(request, unquote(object_id))
        if obj.preflight:
            return HttpResponseRedirect('push/')
        if '_save_and_push' not in request.POST:
            return super(BatchAdmin, self).change_view(
                request, object_id, extra_context=extra_context)
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
            if hasattr(self, 'inline_instances'):
                inline_instances = self.inline_instances

            else:
                inline_instances = []

            zipped_formsets = zip(self.get_formsets(request, new_object),
                                  inline_instances)
            for FormSet, inline in zipped_formsets:
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

                change_message = self.construct_change_message(
                    request, form, formsets)
                self.log_change(request, new_object, change_message)

                return HttpResponseRedirect('push/')

        context = {}.update(extra_context)
        return self.render_change_form(request, context, change=True, obj=obj)

    @csrf_protect_m
    @transaction.commit_on_success
    def pushing_view(self, request, object_id, form_url='', extra_context=None):
        batch_push_item_pk = request.POST.get('push-batch-item')
        if request.is_ajax() and batch_push_item_pk:
            batch_push_item = BatchPushItem.objects.get(pk=batch_push_item_pk)
            if not batch_push_item.batch.first_push_attempt:
                batch_push_item.batch.first_push_attempt = datetime.now()
                batch_push_item.batch.save()
            client.push_one(batch_push_item)
            return render_to_response('admin/nudge/batch/_batch_item_row.html',
                                      {'batch_item': batch_push_item})

        batch = self.model.objects.get(pk=object_id)

        if request.method == 'POST' and 'abort_preflight' in request.POST:
            BatchPushItem.objects.filter(batch=batch).delete()
            batch.preflight = None
            batch.save()

        if request.method == 'POST' and 'push_now' in request.POST:
            client.push_batch(batch)

        if not batch.preflight:
            return HttpResponseRedirect('../')

        batch_push_items = BatchPushItem.objects.filter(batch=batch)
        context = {'batch_push_items': batch_push_items,
                   'media': mark_safe(self.media)}

        opts = self.model._meta
        app_label = opts.app_label
        return TemplateResponse(request, [
            "admin/%s/%s/push.html" % (app_label, opts.object_name.lower()),
        ], context, current_app=self.admin_site.name)

    def get_urls(self):
        urlpatterns = super(BatchAdmin, self).get_urls()

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
        items_str = request.POST.getlist('changes_in_batch')

        obj.selected_items_packed = json.dumps(items_str)
        if '_save_and_push' in request.POST:
            obj.preflight = datetime.now()
            obj.save()
            for selected_item in obj.selected_items:
                bi = utils.inflate_batch_item(selected_item, obj)
                bi.save()
            request.POST['_continue'] = 1
        obj.save()


admin.site.register(Batch, BatchAdmin)
