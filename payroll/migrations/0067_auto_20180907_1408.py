# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-09-07 21:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0066_auto_20180907_1356'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nextofkin',
            name='relationship',
            field=models.CharField(choices=[('H', 'Husband'), ('W', 'Wife'), ('B', 'Brother'), ('S', 'Sister'), ('M', 'Mother'), ('F', 'Father'), ('S', 'Son'), ('D', 'Daughter'), ('C', 'Cousin'), ('N', 'Niece'), ('F', 'Friend')], default=False, max_length=2),
        ),
    ]