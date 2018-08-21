# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-02-15 12:33
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0028_auto_20170209_1500'),
        ('leave', '0008_leaverequest_leave_period'),
    ]

    operations = [
        migrations.CreateModel(
            name='LeaveRequestMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('removed', models.DateTimeField(blank=True, default=None, editable=False, null=True)),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('comment', models.TextField(blank=True)),
                ('leave_status', models.CharField(choices=[('P', 'Pending'), ('A', 'Approved'), ('R', 'Rejected')], default='P', max_length=2)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
        ),
        migrations.RemoveField(
            model_name='leaverequeststatus',
            name='request',
        ),
        migrations.RemoveField(
            model_name='leaverequeststatus',
            name='reviewed_by',
        ),
        migrations.AddField(
            model_name='leaverequest',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='LeaveRequestStatus',
        ),
        migrations.AddField(
            model_name='leaverequestmessage',
            name='request',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='leave.LeaveRequest'),
        ),
        migrations.AddField(
            model_name='leaverequestmessage',
            name='reviewer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payroll.EmployeeProfile'),
        ),
    ]
