# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-01-24 12:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0009_auto_20170124_0941'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='educationlevel',
            options={'ordering': ('id',)},
        ),
        migrations.AlterField(
            model_name='certification',
            name='name',
            field=models.CharField(max_length=512, unique=True),
        ),
        migrations.AlterField(
            model_name='language',
            name='name',
            field=models.CharField(max_length=512, unique=True),
        ),
    ]
