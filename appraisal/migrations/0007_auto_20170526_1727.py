# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-05-26 14:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appraisal', '0006_auto_20170526_1723'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appraisalmeasure',
            name='definition',
            field=models.TextField(max_length=512),
        ),
    ]
