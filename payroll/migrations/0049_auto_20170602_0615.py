# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-06-02 03:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0048_auto_20170531_1601'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employeeprofile',
            name='service_line',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employee_profiles', to='payroll.ServiceLine'),
        ),
    ]