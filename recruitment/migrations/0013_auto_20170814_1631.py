# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-08-14 13:31
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0053_auto_20170811_1818'),
        ('recruitment', '0012_auto_20170814_1321'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobApplicationShortList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.RenameField(
            model_name='jobapplication',
            old_name='education_summary',
            new_name='education_fields',
        ),
        migrations.AddField(
            model_name='jobapplication',
            name='employee',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='job_applications', to='payroll.EmployeeProfile'),
        ),
        migrations.AddField(
            model_name='jobapplicationshortlist',
            name='application',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='short_listed', to='recruitment.JobApplication'),
        ),
    ]