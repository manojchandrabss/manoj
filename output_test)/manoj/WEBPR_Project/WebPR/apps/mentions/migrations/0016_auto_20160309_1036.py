# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-03-09 10:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mentions', '0015_auto_20160302_0522'),
    ]

    operations = [

        migrations.AddField(
            model_name='rating',
            name='open_todo',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='rating',
            name='solved_todo',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]