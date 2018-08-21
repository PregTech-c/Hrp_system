# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-05-25 03:41
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0041_auto_20170525_0636'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='employeeprofile',
            options={'ordering': ['user__last_name'], 'permissions': (('hrp_configure_company', 'Can edit company Info [Administration > Company Info]'), ('hrp_configure_pim', 'Can configure Personnel Info [Administration > Persionnel Info]'), ('hrp_manage_employee_info', 'Can manage employees (PIM -> Employees -> Add/Update)'), ('hrp_configure_leave', 'Can configure Leave Info [Administration > Leave]'), ('hrp_handle_leave_requests', 'Can authorize leave days'), ('hrp_configure_payroll', 'Can configure Payroll Info [Administration > Payroll]'), ('hrp_manage_payroll', 'Can generate/edit payroll (Payroll -> Payroll Cycles -> Add)'), ('hrp_authorize_payroll', 'Can authorize payrolls'), ('hrp_view_payroll_reports', 'Can view payroll reports (Payroll -> Reports -> Summary, Bank, ...)'), ('hrp_view_system_reports', 'Can view system reports (System -> Reports -> User Activity, ...'), ('hrp_configure_appraisal', 'Can manage Appraisal settings [Administration > Appraisal]'))},
        ),
    ]
