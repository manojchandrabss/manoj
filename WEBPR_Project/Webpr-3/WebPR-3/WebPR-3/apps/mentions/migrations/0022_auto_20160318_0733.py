# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-03-18 07:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mentions', '0021_auto_20160315_0135'),
    ]

    operations = [

        migrations.AddField(
            model_name='rating',
            name='month',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='rating',
            name='week',
            field=models.IntegerField(blank=True, null=True),
        ),

    ]