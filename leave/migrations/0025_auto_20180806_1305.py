# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-08-06 20:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('leave', '0024_auto_20180806_1258'),
    ]

    operations = [
        migrations.AlterField(
            model_name='holiday',
            name='country',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='country', to='countries.Country'),
        ),
    ]
