# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-05-25 15:17
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0045_auto_20170525_1718'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='position',
            name='removed',
        ),
    ]