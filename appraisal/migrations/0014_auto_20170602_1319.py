# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-06-02 10:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appraisal', '0013_auto_20170602_1256'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employeeappraisalmeasure',
            name='rating',
            field=models.IntegerField(null=True),
        ),
    ]