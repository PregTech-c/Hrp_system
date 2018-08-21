# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-08-17 18:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0084_auto_20180802_1702'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='employeerecurringadjustment',
            options={'ordering': ['-id']},
        ),
        migrations.AddField(
            model_name='employeerecurringadjustment',
            name='sort_by',
            field=models.CharField(blank=True, choices=[(0, 'Employee'), (1, 'Sercive line'), (2, 'Position')], default='0', max_length=2),
        ),
    ]