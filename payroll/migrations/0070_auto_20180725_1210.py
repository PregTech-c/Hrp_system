# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-07-25 19:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0069_delete_relationship'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nextofkin',
            name='relationship',
            field=models.CharField(choices=[('H', 'Husband'), ('W', 'Wife'), ('B', 'Brother'), ('S', 'Sister'), ('M', 'Mother'), ('F', 'Father'), ('S', 'Son'), ('D', 'Daughter')], default='SELECT', max_length=2),
        ),
    ]
