# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-10-27 15:33
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('asset', '0008_auto_20171027_1754'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assetissuance',
            name='asset_status',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='issues', to='asset.AssetStatus'),
        ),
        migrations.AlterField(
            model_name='assetissuance',
            name='employee',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='asset.Asset'),
        ),
    ]
