# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):
    depends_on = (
        ('reversion', '0001_initial'),
    )

    def forwards(self, orm):
        # Adding model 'BatchPushItem'
        db.create_table('nudge_batchpushitem', (
            ('id',
             self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('batch', self.gf('django.db.models.fields.related.ForeignKey')(
                to=orm['nudge.Batch'])),
            ('version', self.gf('django.db.models.fields.related.ForeignKey')(
                to=orm['reversion.Version'])),
            ('last_tried',
             self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('success',
             self.gf('django.db.models.fields.BooleanField')(default=False)),
            ))
        db.send_create_signal('nudge', ['BatchPushItem'])

        # Adding model 'Batch'
        db.create_table('nudge_batch', (
            ('id',
             self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title',
             self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('description',
             self.gf('django.db.models.fields.TextField')(blank=True)),
            ('start_date', self.gf('django.db.models.fields.DateField')(
                default=datetime.datetime(2012, 9, 13, 0, 0))),
            ('created',
             self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True,
                 blank=True)),
            ('updated',
             self.gf('django.db.models.fields.DateTimeField')(auto_now=True,
                 blank=True)),
            ('preflight',
             self.gf('django.db.models.fields.DateTimeField')(null=True,
                 blank=True)),
            ('first_push_attempt',
             self.gf('django.db.models.fields.DateTimeField')(null=True,
                 blank=True)),
            ('selected_items_packed',
             self.gf('django.db.models.fields.TextField')(default='[]')),
            ))
        db.send_create_signal('nudge', ['Batch'])

        # Adding model 'PushHistoryItem'
        db.create_table('nudge_pushhistoryitem', (
            ('id',
             self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('batch', self.gf('django.db.models.fields.related.ForeignKey')(
                to=orm['nudge.Batch'], on_delete=models.PROTECT)),
            ('created',
             self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True,
                 blank=True)),
            ('http_result',
             self.gf('django.db.models.fields.IntegerField')(null=True,
                 blank=True)),
            ))
        db.send_create_signal('nudge', ['PushHistoryItem'])

        # Adding model 'BatchItem'
        db.create_table('nudge_batchitem', (
            ('id',
             self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('object_id', self.gf('django.db.models.fields.IntegerField')()),
            ('version', self.gf('django.db.models.fields.related.ForeignKey')(
                to=orm['reversion.Version'])),
            ('batch', self.gf('django.db.models.fields.related.ForeignKey')(
                to=orm['nudge.Batch'])),
            ))
        db.send_create_signal('nudge', ['BatchItem'])


    def backwards(self, orm):
        # Deleting model 'BatchPushItem'
        db.delete_table('nudge_batchpushitem')

        # Deleting model 'Batch'
        db.delete_table('nudge_batch')

        # Deleting model 'PushHistoryItem'
        db.delete_table('nudge_pushhistoryitem')

        # Deleting model 'BatchItem'
        db.delete_table('nudge_batchitem')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': (
            'django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [],
                     {'unique': 'True', 'max_length': '80'}),
            'permissions': (
            'django.db.models.fields.related.ManyToManyField', [],
            {'to': "orm['auth.Permission']", 'symmetrical': 'False',
             'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {
            'ordering': "('content_type__app_label', 'content_type__model', 'codename')",
            'unique_together': "(('content_type', 'codename'),)",
            'object_name': 'Permission'},
            'codename': (
            'django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [],
                             {'to': "orm['contenttypes.ContentType']"}),
            'id': (
            'django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': (
            'django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [],
                            {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [],
                      {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [],
                           {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [],
                       {'to': "orm['auth.Group']", 'symmetrical': 'False',
                        'blank': 'True'}),
            'id': (
            'django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': (
            'django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': (
            'django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': (
            'django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [],
                           {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [],
                          {'max_length': '30', 'blank': 'True'}),
            'password': (
            'django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': (
            'django.db.models.fields.related.ManyToManyField', [],
            {'to': "orm['auth.Permission']", 'symmetrical': 'False',
             'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [],
                         {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)",
                     'unique_together': "(('app_label', 'model'),)",
                     'object_name': 'ContentType',
                     'db_table': "'django_content_type'"},
            'app_label': (
            'django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': (
            'django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': (
            'django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': (
            'django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'nudge.batch': {
            'Meta': {'object_name': 'Batch'},
            'created': ('django.db.models.fields.DateTimeField', [],
                        {'auto_now_add': 'True', 'blank': 'True'}),
            'description': (
            'django.db.models.fields.TextField', [], {'blank': 'True'}),
            'first_push_attempt': ('django.db.models.fields.DateTimeField', [],
                                   {'null': 'True', 'blank': 'True'}),
            'id': (
            'django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'preflight': ('django.db.models.fields.DateTimeField', [],
                          {'null': 'True', 'blank': 'True'}),
            'selected_items_packed': (
            'django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'start_date': ('django.db.models.fields.DateField', [],
                           {'default': 'datetime.datetime(2012, 9, 13, 0, 0)'}),
            'title': (
            'django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'updated': ('django.db.models.fields.DateTimeField', [],
                        {'auto_now': 'True', 'blank': 'True'})
        },
        'nudge.batchitem': {
            'Meta': {'object_name': 'BatchItem'},
            'batch': ('django.db.models.fields.related.ForeignKey', [],
                      {'to': "orm['nudge.Batch']"}),
            'id': (
            'django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {}),
            'version': ('django.db.models.fields.related.ForeignKey', [],
                        {'to': "orm['reversion.Version']"})
        },
        'nudge.batchpushitem': {
            'Meta': {'object_name': 'BatchPushItem'},
            'batch': ('django.db.models.fields.related.ForeignKey', [],
                      {'to': "orm['nudge.Batch']"}),
            'id': (
            'django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_tried': (
            'django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'success': (
            'django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'version': ('django.db.models.fields.related.ForeignKey', [],
                        {'to': "orm['reversion.Version']"})
        },
        'nudge.pushhistoryitem': {
            'Meta': {'object_name': 'PushHistoryItem'},
            'batch': ('django.db.models.fields.related.ForeignKey', [],
                      {'to': "orm['nudge.Batch']",
                       'on_delete': 'models.PROTECT'}),
            'created': ('django.db.models.fields.DateTimeField', [],
                        {'auto_now_add': 'True', 'blank': 'True'}),
            'http_result': ('django.db.models.fields.IntegerField', [],
                            {'null': 'True', 'blank': 'True'}),
            'id': (
            'django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'reversion.revision': {
            'Meta': {'object_name': 'Revision'},
            'comment': (
            'django.db.models.fields.TextField', [], {'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [],
                             {'auto_now_add': 'True', 'blank': 'True'}),
            'id': (
            'django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manager_slug': ('django.db.models.fields.CharField', [],
                             {'default': "'default'", 'max_length': '200',
                              'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [],
                     {'to': "orm['auth.User']", 'null': 'True',
                      'blank': 'True'})
        },
        'reversion.version': {
            'Meta': {'object_name': 'Version'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [],
                             {'to': "orm['contenttypes.ContentType']"}),
            'format': (
            'django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': (
            'django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.TextField', [], {}),
            'object_id_int': ('django.db.models.fields.IntegerField', [],
                              {'db_index': 'True', 'null': 'True',
                               'blank': 'True'}),
            'object_repr': ('django.db.models.fields.TextField', [], {}),
            'revision': ('django.db.models.fields.related.ForeignKey', [],
                         {'to': "orm['reversion.Revision']"}),
            'serialized_data': ('django.db.models.fields.TextField', [], {}),
            'type': ('django.db.models.fields.PositiveSmallIntegerField', [],
                     {'db_index': 'True'})
        }
    }

    complete_apps = ['nudge']
