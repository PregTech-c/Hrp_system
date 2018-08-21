# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-02-08 17:07
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0023_auto_20170208_0607'),
    ]

    operations = [
        migrations.AddField(
            model_name='employeeprofile',
            name='documents',
            field=models.FileField(blank=True, null=True, upload_to=b'/tmp/'),
        ),
        migrations.AlterField(
            model_name='employeeprofile',
            name='next_of_kin',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='payroll.NextOfKin'),
        ),
    ]
