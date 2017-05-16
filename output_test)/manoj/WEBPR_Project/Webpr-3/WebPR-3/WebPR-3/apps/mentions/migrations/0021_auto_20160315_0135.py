# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-03-15 01:35
from __future__ import unicode_literals

from django.db import migrations
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('mentions', '0020_auto_20160315_0131'),
    ]

    operations = [
        migrations.AddField(
            model_name='rating',
            name='created',
            field=model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created'),
        ),
        migrations.AddField(
            model_name='rating',
            name='modified',
            field=model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified'),
        ),

    ]
