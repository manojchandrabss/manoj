# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-03-02 05:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mentions', '0012_auto_20160301_0645'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='merchant',
            name='ceo',
        ),
        migrations.AddField(
            model_name='merchant',
            name='contact_info',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
