# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-08-03 20:37
from __future__ import unicode_literals

from django.db import migrations, models
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('leave', '0015_remove_leavetype_positions'),
    ]

    operations = [
        migrations.CreateModel(
            name='Foo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', django_countries.fields.CountryField(max_length=2)),
            ],
        ),
    ]
