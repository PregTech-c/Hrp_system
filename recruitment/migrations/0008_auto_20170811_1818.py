# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-08-11 15:18
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recruitment', '0007_auto_20170811_1534'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='vacancy',
            options={'ordering': ['-due_date']},
        ),
    ]