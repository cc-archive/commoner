
from south.db import db
from django.db import models
from commoner.log.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding field 'LogEntry.send_email'
        db.add_column('log_logentry', 'send_email', orm['log.LogEntry:send_email'])
        
    
    
    def backwards(self, orm):
        
        # Deleting field 'LogEntry.send_email'
        db.delete_column('log_logentry', 'send_email')
        
    
    
    models = {
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'log.logentry': {
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'log_entries'", 'to': "orm['contenttypes.ContentType']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'message_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'send_email': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'})
        }
    }
    
    complete_apps = ['log']
