# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-02-15 10:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('leave', '0007_auto_20170215_1008'),
    ]

    operations = [
        migrations.AddField(
            model_name='leaverequest',
            name='leave_period',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='leave_requests', to='leave.LeavePeriod'),
            preserve_default=False,
        ),
    ]
