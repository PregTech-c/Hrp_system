from __future__ import unicode_literals

from django.db import models
from django_permanent.models import PermanentModel
from payroll.models import Position
from payroll.models import EmployeeProfile, ServiceLine

from auditlog.registry import auditlog
from auditlog.models import AuditlogHistoryField

from datetime import datetime
#class TargetMeasurementUnit(models.Model):
#    UNIT_CHOICES = (
#        ('NUMBER', 'Number'),
#        ('PERCENTAGE', 'Percentage'),
#    )
#    name = models.CharField(max_length=32, choices=UNIT_CHOICES)

class Appraisal(PermanentModel):
    class Meta:
        ordering = ('status', 'start_date')

    STATUS_CHOICES = (
        ('0', 'Open'),
        ('1', 'Closed')
    )
    PERFORMANCE_CHOICES = (
        ('0', 'Failure'),
        ('1', 'Improvement Needed'),
        ('2', 'Excellent'),
        ('3', 'Exceptional')
    )
    start_date = models.DateField()
    end_date = models.DateField()
    due_date = models.DateField(null=True, blank=True)
    employee_profile = models.ForeignKey(EmployeeProfile, null=True, blank=True)
    service_line = models.ForeignKey(ServiceLine, null=True, blank=True,
        related_name="appraisal")
    description = models.CharField(max_length=32,
        help_text='(e.g. 1st quarter 2017)') # e.g. 1st Quarter
#    comment = models.TextField(blank=True)
    performance_classification = models.CharField(max_length=1, choices=PERFORMANCE_CHOICES,
        default=PERFORMANCE_CHOICES[0][0], blank=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES,
        default=STATUS_CHOICES[0][0], blank=True)

    def __str__(self):
#        return self.description
        return "{} - {}".format(
            datetime.strftime(self.start_date, '%d %b %Y'),
            datetime.strftime(self.end_date, '%d %b %Y')
        )

class AppraisalParameter(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    is_core = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class AppraisalMeasure(models.Model):
    parameter = models.ForeignKey(AppraisalParameter,
        related_name='measure_definitions')
    position = models.ForeignKey(Position,
        related_name='measure_definitions')
    service_line = models.ForeignKey(ServiceLine,
        related_name='measure_definitions')
    definition = models.TextField(max_length=512)
    min_rating = models.IntegerField()
    max_rating = models.IntegerField()
    description = models.TextField(blank=True)

    def __str__(self):
        return self.definition

class EmployeePendingAppraisalManager(models.Manager):
    def get_queryset(self, **kwargs):
        return super(EmployeePendingAppraisalManager, self
            ).get_queryset().exclude(status__in=['1'])

class EmployeeAppraisal(models.Model):
    class Meta:
        ordering = ('-id',)

    STATUS_CHOICES = (
        ('0', 'Complete'),
        ('1', 'Pending'),
        ('2', 'Canceled'),
        ('3', 'In progress')
    )

    appraisal = models.ForeignKey(Appraisal, related_name='employee_appraisals',
        on_delete=models.CASCADE)
    employee_profile = models.ForeignKey(EmployeeProfile,
        related_name='appraisals')
    status = models.CharField(max_length=1, choices=STATUS_CHOICES,
        default=STATUS_CHOICES[1][0], blank=True)
    on_open_remarks = models.TextField(null=True, blank=True)
    on_close_remarks = models.TextField(null=True, blank=True)
    closed_on = models.DateTimeField(null=True, blank=True)

    objects = models.Manager()
    pending_appraisals = EmployeePendingAppraisalManager()

    history = AuditlogHistoryField()

    @property
    def is_complete(self):
        if self.status in ['0', '2']:
            return True
        return False

    def get_has_appraisal(self):
        if self.is_complete:
            return None
        return self.flows.order_by('-id')[0].to_reviewer


    def get_total_answered(self, **kwargs):
        return self.measures.filter(
            rating__isnull=False,
            comment__isnull=False,
            reviewer=kwargs.get('reviewer')
            ).count()

    def get_average_rating(self, reviewer=None):
        sum_ratios = 0
        count = 0
        q=models.Q()
        if reviewer is not None:
            q=models.Q(reviewer=reviewer)

        measures = self.measures.filter(q)
        for measure in measures:
            if measure.rating is not None:
                sum_ratios += float(measure.rating) / measure.measure.max_rating
                count += 1
        avg_rating = sum_ratios/count * 100

        return round(avg_rating)

auditlog.register(EmployeeAppraisal)


class EmployeeAppraisalMeasure(models.Model):
    employee_appraisal = models.ForeignKey(EmployeeAppraisal,
        related_name='measures', blank=True)
    measure = models.ForeignKey(AppraisalMeasure, related_name='reviews',
        blank=True)
    rating = models.IntegerField(null=True)
    comment = models.TextField(blank=True)
    reviewer = models.ForeignKey(EmployeeProfile, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_self_appraisal(self):

        return self.employee_appraisal.measures.filter(
            employee_appraisal=self.employee_appraisal,
            measure=self.measure
        ).order_by('id')[0]

    def get_supervisor_appraisal(self):

        measures = self.employee_appraisal.measures.filter(
            employee_appraisal=self.employee_appraisal,
            measure=self.measure
        )

        if measures.count() > 1:
            return measures.order_by('-id')[0]
        return None

    history = AuditlogHistoryField()

auditlog.register(EmployeeAppraisalMeasure)

class EmployeeAppraisalFlow(models.Model):
    employee_appraisal = models.ForeignKey(EmployeeAppraisal,
        related_name="flows")
    from_reviewer = models.ForeignKey(EmployeeProfile,
        related_name="appraisal_submissions", default=1)
    to_reviewer = models.ForeignKey(EmployeeProfile,
        related_name="appraisal_receipts")
    comment = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class PerformanceClassification(models.Model):
        STATUS_CHOICES = (
            ('0', 'Failure'),
            ('1', 'Improvement Needed'),
            ('2', 'Excellent'),
            ('3', 'Exceptional')
        )
    #    appraisal = models.ForeignKey(Appraisal, related_name='performance_classification',
    #        on_delete=models.CASCADE)
    #    employee_profile = models.ForeignKey(EmployeeProfile,
    #        related_name='performance_classification')
        classification = models.CharField(max_length=1, choices=STATUS_CHOICES,
            default=STATUS_CHOICES[1][0], blank=True)
        comment = models.TextField(null=True)
