# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-12-02 09:16
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('asset', '0013_auto_20171202_1159'),
    ]

    operations = [
        migrations.RenameField(
            model_name='assetissuance',
            old_name='return_comment',
            new_name='comment',
        ),
    ]
