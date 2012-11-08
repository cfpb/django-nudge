from datetime import date
from django.db import models

try:
    import simplejson as json
except ImportError:
    import json


class BatchPushItem(models.Model):
    batch = models.ForeignKey('Batch')
    version = models.ForeignKey('reversion.Version')
    last_tried = models.DateTimeField(null=True)
    success = models.BooleanField(default=False)

    def __unicode__(self):
        return unicode(self.version)

    def version_type_string(self):
        return VERSION_TYPE_LOOKUP[self.version.type]


def default_batch_start_date():
    # date last completed batch pushed
    # or date of earliest revision
    # or today
    return date.today()


class Batch(models.Model):
    title = models.CharField(max_length=1000)
    description = models.TextField(blank=True)
    start_date = models.DateField(default=default_batch_start_date)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    preflight = models.DateTimeField(null=True, blank=True)
    first_push_attempt = models.DateTimeField(null=True, blank=True)
    selected_items_packed = models.TextField(default=json.dumps([]))

    def __unicode__(self):
        return u'%s' % self.title

    def is_valid(self, test_only=True):
        return True

    @property
    def selected_items(self):
        if not hasattr(self, '_selected_items'):
            self._selected_items = json.loads(self.selected_items_packed)
        return self._selected_items

    class Meta:
        verbose_name_plural = 'batches'
        permissions = (
            ('push_batch', 'Can push batches'),
        )


class PushHistoryItem(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)
    http_result = models.IntegerField(blank=True, null=True)


class BatchItem(models.Model):
    object_id = models.IntegerField()
    version = models.ForeignKey('reversion.Version')
    batch = models.ForeignKey(Batch)

    def __unicode__(self):
        return u'%s' % self.version.object_repr


from nudge.utils import VERSION_TYPE_LOOKUP
