# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-08-17 18:49
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('leave', '0025_auto_20180806_1305'),
    ]

    operations = [
        migrations.AddField(
            model_name='leaverequest',
            name='reports_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='leave.LeaveRequest'),
        ),
    ]
