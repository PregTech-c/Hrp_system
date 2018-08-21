# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-06-02 09:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('appraisal', '0011_auto_20170602_0621'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employeeappraisal',
            name='status',
            field=models.CharField(blank=True, choices=[('0', 'Complete'), ('1', 'Pending'), ('2', 'Canceled'), ('3', 'In progress')], default='3', max_length=1),
        ),
        migrations.AlterField(
            model_name='employeeappraisalmeasure',
            name='measure',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='measures', to='appraisal.AppraisalMeasure'),
        ),
    ]
