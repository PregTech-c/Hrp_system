# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-07-20 05:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appraisal', '0023_employeeappraisalmeasure_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='appraisal',
            name='comment',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='appraisal',
            name='description',
            field=models.TextField(),
        ),
    ]
