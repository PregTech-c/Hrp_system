# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-07-20 22:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appraisal', '0027_auto_20170720_1320'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employeeappraisalflow',
            name='comment',
            field=models.TextField(null=True),
        ),
    ]
