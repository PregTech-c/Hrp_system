# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-11-08 05:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0058_auto_20171108_0540'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employeerecurringadjustment',
            name='allowance',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='recurring_allowances', to='payroll.AllowanceType'),
        ),
        migrations.AlterField(
            model_name='employeerecurringadjustment',
            name='deduction',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='recurring_deductions', to='payroll.DeductionType'),
        ),
    ]