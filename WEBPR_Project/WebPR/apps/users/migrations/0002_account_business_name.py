# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-04 04:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='business_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]