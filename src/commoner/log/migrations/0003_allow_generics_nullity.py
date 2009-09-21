
from south.db import db
from django.db import models
from commoner.log.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Changing field 'LogEntry.object_id'
        # (to signature: django.db.models.fields.PositiveIntegerField(null=True, blank=True))
        db.alter_column('log_logentry', 'object_id', orm['log.logentry:object_id'])
        
        # Changing field 'LogEntry.content_type'
        # (to signature: django.db.models.fields.related.ForeignKey(blank=True, null=True, to=orm['contenttypes.ContentType']))
        db.alter_column('log_logentry', 'content_type_id', orm['log.logentry:content_type'])
        
    
    
    def backwards(self, orm):
        
        # Changing field 'LogEntry.object_id'
        # (to signature: django.db.models.fields.PositiveIntegerField())
        db.alter_column('log_logentry', 'object_id', orm['log.logentry:object_id'])
        
        # Changing field 'LogEntry.content_type'
        # (to signature: django.db.models.fields.related.ForeignKey(to=orm['contenttypes.ContentType']))
        db.alter_column('log_logentry', 'content_type_id', orm['log.logentry:content_type'])
        
    
    
    models = {
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'log.logentry': {
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'log_entries'", 'blank': 'True', 'null': 'True', 'to': "orm['contenttypes.ContentType']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'message_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'send_email': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'})
        }
    }
    
    complete_apps = ['log']
