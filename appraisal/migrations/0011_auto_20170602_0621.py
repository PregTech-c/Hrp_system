# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-06-02 03:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('appraisal', '0010_auto_20170602_0545'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employeeappraisalflow',
            name='employee_appraisal',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='flows', to='appraisal.EmployeeAppraisal'),
        ),
    ]
