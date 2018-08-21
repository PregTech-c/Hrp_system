# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-07-25 18:23
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0065_auto_20180725_1009'),
    ]

    operations = [
        migrations.CreateModel(
            name='Relationship',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('removed', models.DateTimeField(blank=True, default=None, editable=False, null=True)),
                ('relationship', models.CharField(max_length=256)),
            ],
            options={
                'ordering': ('id',),
            },
        ),
        migrations.AlterField(
            model_name='nextofkin',
            name='relationship',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='payroll.Relationship'),
        ),
        migrations.AlterUniqueTogether(
            name='relationship',
            unique_together=set([('relationship',)]),
        ),
    ]
