# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-03-15 01:31
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mentions', '0019_auto_20160314_1013'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rating',
            name='created',
        ),
        migrations.RemoveField(
            model_name='rating',
            name='modified',
        ),
    ]
