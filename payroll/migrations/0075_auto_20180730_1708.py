# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-07-31 00:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0074_auto_20180730_1001'),
    ]

    operations = [
        migrations.AlterField(
            model_name='serviceline',
            name='service_line_type',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='lines', to='payroll.ServiceLineType'),
        ),
    ]
