# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-08-17 13:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recruitment', '0023_auto_20170817_1526'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vacancy',
            name='minimum_education',
            field=models.CharField(blank=True, choices=[(b'PRIMARY', b'Primary'), (b'OLEVEL', b"O'Level"), (b'ALEVEL', b"A'Level"), (b'TERTIARY', b'Tertiary'), (b'UNIVERSITY', b'University')], max_length=8, null=True),
        ),
        migrations.AlterField(
            model_name='vacancy',
            name='required_gender',
            field=models.CharField(choices=[('A', 'Any'), ('M', 'Male'), ('F', 'Female')], default='M', max_length=1),
        ),
    ]
