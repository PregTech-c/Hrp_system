# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-07-25 17:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0064_allowancetype_is_taxed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='educationlevel',
            name='level',
            field=models.CharField(choices=[('PRIMARY', 'Primary'), ('OLEVEL', "O'Level"), ('ALEVEL', "A'Level"), ('TERTIARY', 'Tertiary'), ('UNIVERSITY', 'University')], max_length=16),
        ),
        migrations.AlterField(
            model_name='employeeprofile',
            name='employee_type',
            field=models.CharField(choices=[('S', 'Salaried'), ('C', 'Consultant')], default=0, max_length=16),
        ),
        migrations.AlterField(
            model_name='employeeprofile',
            name='gender',
            field=models.CharField(choices=[('M', 'Male'), ('F', 'Female')], default=0, max_length=2),
        ),
        migrations.AlterField(
            model_name='employeeprofile',
            name='marital_status',
            field=models.CharField(choices=[('S', 'Single'), ('M', 'Married'), ('D', 'Divorced')], default=('S', 'Single'), max_length=2),
        ),
        migrations.AlterField(
            model_name='employeeprofile',
            name='status',
            field=models.CharField(choices=[('A', 'Active'), ('R', 'Resigned'), ('T', 'Terminated')], default=0, max_length=2),
        ),
    ]
