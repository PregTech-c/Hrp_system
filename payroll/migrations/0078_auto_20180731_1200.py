# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-07-31 19:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0077_auto_20180731_1135'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employeeprofile',
            name='nin',
            field=models.CharField(blank=True, max_length=2),
        ),
    ]
