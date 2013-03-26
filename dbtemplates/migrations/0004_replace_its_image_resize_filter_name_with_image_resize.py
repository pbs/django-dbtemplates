# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.db import router
from dbtemplates.models import Template


class Migration(SchemaMigration):

    no_dry_run = True

    def replace(self, orm, old, new):
        templates = orm.models.get("dbtemplates.template").objects\
                        .db_manager(router.db_for_write(Template)).all()
        for tpl in templates:
            tpl.content = regex_replace(tpl.content, old, new)
            tpl.save()

    def forwards(self, orm):
        self.replace(orm, "its_image_resize", "image_resize")

    def backwards(self, orm):
        self.replace(orm, "image_resize", "its_image_resize")


    models = {
        'dbtemplates.template': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Template', 'db_table': "'django_template'"},
            'content': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_changed': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sites.Site']", 'symmetrical': 'False'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['dbtemplates']
