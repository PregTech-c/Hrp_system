# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-02-14 18:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leave', '0003_auto_20170214_1843'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leavetype',
            name='service_lines',
            field=models.ManyToManyField(blank=True, to='payroll.ServiceLine'),
        ),
    ]
