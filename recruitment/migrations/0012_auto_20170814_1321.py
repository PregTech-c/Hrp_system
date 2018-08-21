# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-08-14 10:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recruitment', '0011_jobapplication_date_of_birth'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobapplication',
            name='remarks',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='jobapplication',
            name='qualification',
            field=models.CharField(blank=True, choices=[('PRIM', 'Primary Level'), ('OLEV', 'Secondary Level'), ('ALEV', 'Advanced Level'), ('DEG', 'Bachelors Degree'), ('DIPL', 'Diploma'), ('MAST', 'Masters Degree'), ('PHD', 'Phd')], max_length=16, null=True),
        ),
    ]