# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-02-14 15:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leave', '0002_auto_20170214_1459'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leavetype',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]
