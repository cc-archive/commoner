
from south.db import db
from django.db import models
from commoner.citations.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Citation'
        db.create_table('citations_citation', (
            ('id', orm['citations.Citation:id']),
            ('cited_url', orm['citations.Citation:cited_url']),
            ('resolved_url', orm['citations.Citation:resolved_url']),
            ('cited_by', orm['citations.Citation:cited_by']),
            ('cited_on', orm['citations.Citation:cited_on']),
            ('license_url', orm['citations.Citation:license_url']),
            ('urlkey', orm['citations.Citation:urlkey']),
        ))
        db.send_create_signal('citations', ['Citation'])
        
        # Adding model 'Reuser'
        db.create_table('citations_reuser', (
            ('id', orm['citations.Reuser:id']),
            ('citation', orm['citations.Reuser:citation']),
            ('url', orm['citations.Reuser:url']),
            ('added_by', orm['citations.Reuser:added_by']),
            ('added_on', orm['citations.Reuser:added_on']),
        ))
        db.send_create_signal('citations', ['Reuser'])
        
        # Adding model 'MetaInfo'
        db.create_table('citations_metainfo', (
            ('id', orm['citations.MetaInfo:id']),
            ('citation', orm['citations.MetaInfo:citation']),
            ('key', orm['citations.MetaInfo:key']),
            ('value', orm['citations.MetaInfo:value']),
            ('added_by', orm['citations.MetaInfo:added_by']),
        ))
        db.send_create_signal('citations', ['MetaInfo'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Citation'
        db.delete_table('citations_citation')
        
        # Deleting model 'Reuser'
        db.delete_table('citations_reuser')
        
        # Deleting model 'MetaInfo'
        db.delete_table('citations_metainfo')
        
    
    
    models = {
        'auth.group': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'unique': 'True'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)"},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '30', 'unique': 'True'})
        },
        'citations.citation': {
            'cited_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'cited_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'cited_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'license_url': ('django.db.models.fields.URLField', [], {'max_length': '255', 'blank': 'True'}),
            'resolved_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'urlkey': ('django.db.models.fields.CharField', [], {'max_length': '5'})
        },
        'citations.metainfo': {
            'added_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'citation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'metainfo'", 'to': "orm['citations.Citation']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'citations.reuser': {
            'added_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'citation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reusers'", 'to': "orm['citations.Citation']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }
    
    complete_apps = ['citations']
