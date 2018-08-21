from __future__ import unicode_literals

from django.db import models
from django.utils import timezone

from payroll.models.employee_models import (ServiceLine, Position,
    EducationLevel, EmployeeProfile)

GENDER_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female')
)

class District(models.Model):
    short_name = models.CharField(max_length=4)
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name

class Vacancy(models.Model):
    VACANCY_TYPE_CHOICES = (
        ('PUB', 'Public'),
        ('INT', 'Internal'),
    )
    GENDER_CHOICES = (
        ('A', 'Any'), ('M', 'Male'), ('F', 'Female')
    )

    class Meta:
        ordering = ['-due_date']

    job_title = models.ForeignKey(Position, related_name='vacancies')
    service_line = models.ForeignKey(ServiceLine, null=True, blank=True)
    reports_to = models.ForeignKey(Position, null=True, blank=True)
    due_date = models.DateField()
    minimum_education = models.CharField(max_length=16,
        choices=EducationLevel.EDUC_LEVEL_CHOICES, null=True, blank=True)
    fields_of_education = models.TextField(null=True,
        blank=True, help_text="Separate with semi-colon (;)")
    skills = models.TextField(max_length=256, null=True, blank=True)
    number_of_positions = models.IntegerField(default=1)
    job_description = models.TextField()
    vacancy_type = models.CharField(max_length=8, choices=VACANCY_TYPE_CHOICES,
        default=VACANCY_TYPE_CHOICES[0][1])
    duty_station = models.ForeignKey(District, null=True, blank=True)
    min_age = models.IntegerField(null=True, blank=True)
    max_age = models.IntegerField(null=True, blank=True)
    experience_years = models.IntegerField(null=True, blank=True)
    required_gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M')

    def __str__(self):
        return self.job_title.name

class EvaluationStage(models.Model):
    STATUS_CHOICES = (('OPEN', 'Open'), ('CLOSED', 'Closed'))
    class Meta:
        unique_together = ('vacancy', 'name')

    vacancy = models.ForeignKey(Vacancy, related_name='evaluation_stages')
    name = models.CharField(max_length=32)
    description = models.CharField(max_length=64)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES,
        default=STATUS_CHOICES[0][0], blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(EmployeeProfile)

    def __str__(self):
        return self.name

class JobApplication(models.Model):
    APPLICATION_SOURCE_CHOICES = (
        ('NP', 'Newspaper'),
        ('REF', 'Referral'),
        ('WEB', 'Website')
    )
    QUALIFICATION_CHOICES = (
        ('PRIM', 'Primary Level'),
        ('OLEV', 'Secondary Level'),
        ('ALEV', 'Advanced Level'),
        ('DEG', 'Bachelors Degree'),
        ('DIPL', 'Diploma'),
        ('MAST', 'Masters Degree'),
        ('PHD', 'Phd'),
    )

    class Meta:
        ordering = ['-id']

    employee = models.ForeignKey(EmployeeProfile,
        related_name="job_applications", null=True, blank=True)
    vacancy = models.ForeignKey(Vacancy, related_name='applications')
    first_name = models.CharField(max_length=32)
    surname = models.CharField(max_length=32)
    other_names = models.CharField(max_length=64, null=True, blank=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M')
#    source = models.CharField(max_length=16, choices=APPLICATION_SOURCE_CHOICES,
#        default='NP')
    email = models.EmailField()
    tel_number = models.CharField(max_length=16)
    qualification = models.CharField(max_length=16,
        choices=QUALIFICATION_CHOICES, null=True, blank=True)
    experience_years = models.DecimalField(decimal_places=1, max_digits=3)
    education_fields = models.TextField()
    remarks = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    evaluation_stage = models.ForeignKey(EvaluationStage, null=True, blank=True)

    @property
    def age_of_applicant(self):
        td = timezone.now().date() - self.date_of_birth
        return int(td.days/365.2425)

    def get_fullname(self):
        return "{} {} {}".format(
            self.surname,
            self.first_name if self.first_name else '',
            self.other_names if self.other_names else ''
        )

def upload_directory(instance, filename):
    return 'payroll/static/uploads/{}/{}'.format(
        'recruitment', filename)

class JobApplicationDocument(models.Model):
    job_application = models.ForeignKey(JobApplication,
        related_name='documents')
    document = models.FileField(upload_to=upload_directory, #'uploads/recrutment/%Y/%m/%d/',
        null=True, blank=True)
    description = models.CharField(max_length=32, blank=True)

    def filename(self):
        import os
        return os.path.basename(self.document.name)
