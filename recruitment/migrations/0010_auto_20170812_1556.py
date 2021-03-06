# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-08-12 12:56
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recruitment', '0009_vacancy_vacancy_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='District',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('short_name', models.CharField(max_length=4)),
                ('name', models.CharField(max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='JobApplication',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=32)),
                ('surname', models.CharField(max_length=32)),
                ('other_names', models.CharField(max_length=64)),
                ('source', models.CharField(choices=[('NP', 'Newspaper'), ('REF', 'Referral'), ('WEB', 'Website')], default='NP', max_length=16)),
                ('email', models.EmailField(max_length=254)),
                ('tel_number', models.CharField(max_length=16)),
                ('qualification', models.CharField(choices=[('NP', 'Newspaper'), ('REF', 'Referral'), ('WEB', 'Website')], default='QUALIFICATION_CHOICES', max_length=16)),
                ('experience_years', models.DecimalField(decimal_places=1, max_digits=3)),
                ('education_summary', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='JobApplicationDocument',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', models.FileField(blank=True, null=True, upload_to='uploads/recrutment/%Y/%m/%d/')),
                ('description', models.CharField(blank=True, max_length=32)),
                ('job_application', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='recruitment.JobApplication')),
            ],
        ),
        migrations.RemoveField(
            model_name='candidate',
            name='job_opening',
        ),
        migrations.RemoveField(
            model_name='candidatedocument',
            name='candidate',
        ),
        migrations.AlterField(
            model_name='vacancy',
            name='vacancy_type',
            field=models.CharField(choices=[('PUB', 'Public'), ('INT', 'Internal')], default='Public', max_length=8),
        ),
        migrations.DeleteModel(
            name='Candidate',
        ),
        migrations.DeleteModel(
            name='CandidateDocument',
        ),
        migrations.AddField(
            model_name='jobapplication',
            name='vacancy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applications', to='recruitment.Vacancy'),
        ),
        migrations.AddField(
            model_name='vacancy',
            name='duty_station',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='recruitment.District'),
        ),
    ]
