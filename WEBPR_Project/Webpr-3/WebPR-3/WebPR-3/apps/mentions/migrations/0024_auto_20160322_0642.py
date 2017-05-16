# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-03-22 06:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mentions', '0023_merge'),
    ]

    operations = [

        migrations.AlterField(
            model_name='category',
            name='code',
            field=models.PositiveSmallIntegerField(null=True, unique=True, verbose_name='SIC'),
        ),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='mention',
            name='mention_text',
            field=models.TextField(null=True),
        ),
        migrations.AlterUniqueTogether(
            name='mention',
            unique_together=set([('merchant', 'mention_text')]),
        ),

    ]