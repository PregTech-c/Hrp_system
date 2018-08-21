# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-06-06 12:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appraisal', '0014_auto_20170602_1319'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employeeappraisal',
            name='status',
            field=models.CharField(blank=True, choices=[('0', 'Complete'), ('1', 'Pending'), ('2', 'Canceled'), ('3', 'In progress')], default='1', max_length=1),
        ),
    ]
