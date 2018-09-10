from __future__ import unicode_literals

from django.apps import AppConfig

class PayrollConfig(AppConfig):
    name = 'payroll'

    def ready(self):
        from .signals import generate_payslips