# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-08-13 22:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('appraisal', '0034_appraisal_performance_classification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appraisal',
            name='service_line',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='appraisal', to='payroll.ServiceLine'),
        ),
    ]
