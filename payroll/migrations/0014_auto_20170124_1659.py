# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-01-24 13:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0013_auto_20170124_1659'),
    ]

    operations = [
        migrations.AlterField(
            model_name='skill',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]