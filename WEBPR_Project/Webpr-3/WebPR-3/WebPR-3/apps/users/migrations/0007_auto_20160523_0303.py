# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-05-23 03:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20160520_0859'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='company_name',
            field=models.CharField(max_length=255),
        ),
    ]
