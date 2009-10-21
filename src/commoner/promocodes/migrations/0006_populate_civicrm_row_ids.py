import sqlalchemy

from south.db import db
from django.db import models
from commoner.promocodes.models import *

class Migration:

    no_dry_run = True
    
    def setUp(self):

        # setup database connectivity
        cividb = sqlalchemy.create_engine('mysql://civicrm:Civicrm.@localhost/civicrm', convert_unicode=True, encoding='latin1') 
        
        metadata = sqlalchemy.MetaData(cividb)
        self.civicontrib = sqlalchemy.Table('civicrm_contribution', metadata, autoload=True)
    
    def forwards(self, orm):
        "Write your forwards migration here"

        self.setUp()
        
        # get all of the previously generated codes that have invoice id's
        codes = orm.PromoCode.objects.exclude(contribution_id__in=['None', ''])

        # walk through the codes and try to populate the contribution id's
        for code in codes:

            try:

                # early codes actually contain the data we want
                civi_id = int(code.contribution_id)
                code.civicrm_id = civi_id
                code.save()

                print "%s migrated column, %d" % (code.code, civi_id,)
                
            except:
                
                contrib = self.civicontrib.select(
                              self.civicontrib.c.invoice_id == code.contribution_id
                          ).execute().fetchone()

                if contrib:
                    code.civicrm_id = int(contrib['id'])
                    code.save()

                    print "%s fetched row id, %d" % (code.code, contrib['id'])

            
    def backwards(self, orm):
        "Write your backwards migration here"

        raise Exception("Uh oh there's no going back!")
    
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
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'promocodes.promocode': {
            'civicrm_id': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '8', 'unique': 'True', 'primary_key': 'True'}),
            'contribution_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'expires': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'recipient': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'recurring_contribution_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'transaction_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'used_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'used_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        }
    }
    
    complete_apps = ['promocodes']
