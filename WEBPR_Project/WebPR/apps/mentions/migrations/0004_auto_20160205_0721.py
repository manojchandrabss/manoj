# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-05 07:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mentions', '0003_auto_20160204_0429'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='mention',
            options={'ordering': ('-created',)},
        ),
        migrations.AlterModelOptions(
            name='todo',
            options={'ordering': ('-created',)},
        ),
        migrations.AddField(
            model_name='todo',
            name='is_closed',
            field=models.BooleanField(default=False),
        ),
    ]
