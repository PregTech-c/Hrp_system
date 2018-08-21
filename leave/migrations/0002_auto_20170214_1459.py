# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-02-14 11:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0028_auto_20170209_1500'),
        ('leave', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Holiday',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('removed', models.DateTimeField(blank=True, default=None, editable=False, null=True)),
                ('name', models.CharField(max_length=64)),
                ('date', models.DateField()),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
        ),
        migrations.CreateModel(
            name='LeaveRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('removed', models.DateTimeField(blank=True, default=None, editable=False, null=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('comment', models.TextField()),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payroll.EmployeeProfile')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
        ),
        migrations.CreateModel(
            name='LeaveType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('removed', models.DateTimeField(blank=True, default=None, editable=False, null=True)),
                ('name', models.CharField(max_length=64)),
                ('no_of_days', models.DecimalField(decimal_places=1, default=0, help_text='Maximum number of leave days within a leave period.', max_digits=4)),
                ('days_carried_forward', models.DecimalField(decimal_places=1, default=0, help_text='If days from the previous leave periods are carried over, enter maximum number or percentage. 0 for None.', max_digits=4)),
                ('active', models.BooleanField(default=True)),
                ('gender', models.CharField(blank=True, choices=[('A', 'Any'), ('M', 'Male'), ('F', 'Female')], default='A', max_length=2)),
                ('description', models.TextField()),
                ('positions', models.ManyToManyField(to='payroll.Position')),
                ('service_lines', models.ManyToManyField(to='payroll.ServiceLine')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
        ),
        migrations.AddField(
            model_name='leaverequest',
            name='leave_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='leave.LeaveType'),
        ),
    ]