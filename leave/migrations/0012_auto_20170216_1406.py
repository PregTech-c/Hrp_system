# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-02-16 11:06
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leave', '0011_auto_20170216_1404'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='LeaveRequestApplication',
            new_name='LeaveApplication',
        ),
    ]
