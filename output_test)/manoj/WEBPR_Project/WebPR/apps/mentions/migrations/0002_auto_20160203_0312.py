# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-03 03:12
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('mentions', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='todo',
            name='user',
            field=models.ForeignKey(blank=True, null=True,
                                    on_delete=django.db.models.deletion.CASCADE,
                                    to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='rating',
            name='merchant',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='mentions.Merchant'),
        ),
        migrations.AddField(
            model_name='merchant',
            name='category',
            field=models.ForeignKey(blank=True, null=True,
                                    on_delete=django.db.models.deletion.CASCADE,
                                    to='mentions.Category'),
        ),
        migrations.AddField(
            model_name='mention',
            name='merchant',
            field=models.ForeignKey(blank=True, null=True,
                                    on_delete=django.db.models.deletion.CASCADE,
                                    to='mentions.Merchant'),
        ),
        migrations.AlterUniqueTogether(
            name='rating',
            unique_together=set([('week', 'year', 'merchant')]),
        ),
    ]
