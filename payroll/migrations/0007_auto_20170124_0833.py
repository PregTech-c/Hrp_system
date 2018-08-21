# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-01-24 05:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0006_auto_20170124_0831'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='certification',
            options={'base_manager_name': 'objects'},
        ),
        migrations.AlterModelOptions(
            name='language',
            options={'base_manager_name': 'objects'},
        ),
        migrations.AlterModelOptions(
            name='membership',
            options={'base_manager_name': 'objects'},
        ),
        migrations.AlterModelOptions(
            name='skill',
            options={'base_manager_name': 'objects'},
        ),
        migrations.AddField(
            model_name='certification',
            name='removed',
            field=models.DateTimeField(blank=True, default=None, editable=False, null=True),
        ),
        migrations.AddField(
            model_name='educationlevel',
            name='removed',
            field=models.DateTimeField(blank=True, default=None, editable=False, null=True),
        ),
        migrations.AddField(
            model_name='language',
            name='removed',
            field=models.DateTimeField(blank=True, default=None, editable=False, null=True),
        ),
        migrations.AddField(
            model_name='membership',
            name='removed',
            field=models.DateTimeField(blank=True, default=None, editable=False, null=True),
        ),
        migrations.AddField(
            model_name='skill',
            name='removed',
            field=models.DateTimeField(blank=True, default=None, editable=False, null=True),
        ),
    ]
