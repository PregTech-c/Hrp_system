# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-08-03 20:56
from __future__ import unicode_literals

from django.db import migrations
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('leave', '0018_auto_20180803_1350'),
    ]

    operations = [
        migrations.AlterField(
            model_name='countryname',
            name='country',
            field=django_countries.fields.CountryField(max_length=746, multiple=True),
        ),
    ]
