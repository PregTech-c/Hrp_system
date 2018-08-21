from django.db import models
from .payroll_models import AllowanceType, DeductionType
from .employee_models import EmployeeProfile
from .hrp_fields import CurrencyField

class EmployeeRecurringAdjustment(models.Model):
    TYPES = ((1, 'Allowance'), (2, 'Deduction'))
    STATUS_CHOICES = ((0, 'Employee'), (1, 'Sercive line'), (2, 'Position'))
    employee = models.ForeignKey(EmployeeProfile,
        related_name='recurring_adjustments')
    allowance = models.ForeignKey(AllowanceType, null=True, blank=True)
    deduction = models.ForeignKey(DeductionType, null=True, blank=True)
    adjustment_type = models.CharField(max_length=4, default=2)
    sort_by = models.CharField(max_length=2, choices=STATUS_CHOICES,
        blank=True, default='0')
    comment = models.TextField()
    amount = CurrencyField()
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField()

    def __str__(self):
        return "Recurring {}".format(getattr(self, 'allowance', 'deduction'))

    class Meta:
        ordering = ['-id']
