# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-10 10:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('mentions', '0007_auto_20160210_0954'),
    ]

    operations = [
        migrations.AlterField(
            model_name='todo',
            name='priority',
            field=models.SmallIntegerField(blank=True,
                                           choices=[(0, 'high'), (1, 'middle'),
                                                    (2, 'low')], null=True),
        ),
    ]
