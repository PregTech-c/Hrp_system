# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-08-13 21:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appraisal', '0033_auto_20180813_1332'),
    ]

    operations = [
        migrations.AddField(
            model_name='appraisal',
            name='performance_classification',
            field=models.CharField(blank=True, choices=[('0', 'Failure'), ('1', 'Improvement Needed'), ('2', 'Excellent'), ('3', 'Exceptional')], default='0', max_length=1),
        ),
    ]
