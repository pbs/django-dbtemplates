# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.manager
import django.contrib.sites.managers


class Migration(migrations.Migration):

    dependencies = [
        ('dbtemplates', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='template',
            managers=[
                ('objects', django.db.models.manager.Manager()),
                ('on_site', django.contrib.sites.managers.CurrentSiteManager(b'sites')),
            ],
        ),
    ]
