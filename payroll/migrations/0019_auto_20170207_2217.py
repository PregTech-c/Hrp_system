# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-02-07 19:17
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0018_auto_20170207_2204'),
    ]

    operations = [
        migrations.RenameField(
            model_name='nextofkin',
            old_name='employee',
            new_name='employee_profile',
        ),
    ]
