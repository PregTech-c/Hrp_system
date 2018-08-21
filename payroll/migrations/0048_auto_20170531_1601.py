# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-05-31 13:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0047_auto_20170531_1315'),
    ]

    operations = [
        migrations.AlterField(
            model_name='serviceline',
            name='service_line_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lines', to='payroll.ServiceLineType'),
        ),
    ]
