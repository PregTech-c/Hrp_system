# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-08-01 00:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0080_employeeprofile_national_id_expiry'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employeeprofile',
            name='contract_type',
            field=models.CharField(choices=[('P', 'Permanent'), ('C', 'Contract'), ('I', 'Internship')], default=None, max_length=2),
        ),
    ]
