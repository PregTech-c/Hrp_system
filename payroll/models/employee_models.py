from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext as _

from django_permanent.models import PermanentModel
from auditlog.registry import auditlog
from auditlog.models import AuditlogHistoryField

from .payroll_models import (Payroll, ContractualPay, Payslip, DeductionType,
    AllowanceType)
from .company_models import ServiceLine
from .qualification_models import *

class Nationality(PermanentModel):
#    class Meta:
#        verbose_name = "Nationalities"

    country_code = models.CharField(max_length=2, unique=True)
    name = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return self.name

class SalaryScaleManager(models.Manager):
    def get_scale(self, value):
        q = SalaryScale.objects.filter(
            Q(range_from__isnull=True, range_to__gte=value)|
            Q(range_from__lte=value, range_to__gte=value)|
            Q(range_from__lte=value, range_to__isnull=True))
        return q[0] if q else None

class SalaryScale(models.Model):
    class Meta:
        ordering = ('code',)

    code = models.CharField(max_length=8)
    range_from = models.IntegerField(null=True, blank=True)
    range_to = models.IntegerField(null=True, blank=True)
    objects = SalaryScaleManager()

    def __str__(self):
        return "%s: %s - %s" % (self.code, self.range_from, self.range_to)

class EmployeeTitle(models.Model):
    name = models.CharField(max_length=8, unique=True)

    def __str__(self):
        return self.name

class Bank(models.Model):
    class Meta:
        ordering = ['name']
    name = models.CharField(max_length=32, unique=True)
    phone_number = models.CharField(max_length=32, null=True, blank=True)

    def __str__(self):
        return self.name

class BankBranch(models.Model):
    class Meta:
    	ordering = ['branch_name']
    bank = models.ForeignKey(Bank)
    branch_name = models.CharField(max_length=64)
    sort_code = models.CharField(unique=True, max_length=32)
    phone_number = models.CharField(max_length=32, null=True, blank=True)
    added_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return "%s - %s" % (self.bank.name, self.branch_name)

class Position(models.Model):

    class Meta:
    	ordering = ['name']

    name = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True)
    history = AuditlogHistoryField()

    def __str__(self):
        return self.name
auditlog.register(Position)

class Branch(models.Model):

    class Meta:
        ordering = ['name']

    name = models.CharField(max_length=64, unique=True)
    location = models.TextField(max_length=64, blank=True)

    def __str__(self):
        return self.name

class NextOfKin(PermanentModel):

    RELATIONSHIP_CHOICES = (
        ('H', 'Husband'),
        ('W', 'Wife'),
        ('B', 'Brother'),
        ('S', 'Sister'),
        ('M', 'Mother'),
        ('F', 'Father'),
        ('S', 'Son'),
        ('D', 'Daughter'),
        ('C', 'Cousin'),
        ('N', 'Niece'),
        ('F', 'Friend')
    )

    name = models.CharField(max_length=256)
    contact = models.CharField(max_length=64)
    relationship = models.CharField(max_length=2, choices=RELATIONSHIP_CHOICES, default=False)

    def __str__(self):
        return "{}/{}/{}".format(self.name, self.contact, self.relationship)

def profile_photo_upload_directory(instance, filename):
    return 'payroll/static/uploads/photos/{}/{}'.format(
        instance.user.username, filename)


class Dependants(PermanentModel):
    RELATIONSHIP_CHOICES = (
        ('H', 'Spouse'),
        ('S', 'Son'),
        ('D', 'Daughter'),
        ('B', 'Brother'),
        ('T', 'Sister'),
        ('C', 'Cousin'),
        ('N', 'Niece'),
        ('P', 'Nephew'),
        ('O', 'Other')
    )

    GENDER_CHOICES = (('M', 'Male'), ('F', 'Female'))

    full_name = models.CharField(max_length=64)
    #last_name = models.CharField(max_length=64)
    date_of_birth = models.DateTimeField(null=True, blank=True)
    nin = models.CharField(max_length=24, null=True, blank=True)
    gender = models.CharField(max_length=2, choices=GENDER_CHOICES, default=0)
    relationship = models.CharField(max_length=64, choices=RELATIONSHIP_CHOICES, default=False)
    contact = models.CharField(max_length=64, null=True, blank=True)
    address = models.CharField(max_length=64, null=True, blank=True)
    photo = models.FileField(upload_to=profile_photo_upload_directory, null=True, blank=True)



#    def get_fullname(self):
#        return "{} {} {}".format(
#            self.last_name,
#            self.first_name if self.first_name else ''
        #    self.other_names if self.other_names else ''
#        )

class EmployeeProfile(PermanentModel):
    """Defines extra info for an employee"""
    class Meta:
        ordering = ['user__last_name']
        permissions = (
            ('hrp_configure_company', 'Can edit company Info [Administration > Company Info]'),

            ('hrp_configure_pim', 'Can configure Personnel Info [Administration > Persionnel Info]'),
            ('hrp_manage_employee_info', 'Can manage employees (PIM -> Employees -> Add/Update)'),

            ('hrp_configure_leave', 'Can configure Leave Info [Administration > Leave]'),
            ('hrp_handle_leave_requests', 'Can authorize leave days'),

            ('hrp_configure_payroll', 'Can configure Payroll Info [Administration > Payroll]'),
            ('hrp_manage_payroll', 'Can generate/edit payroll (Payroll -> Payroll Cycles -> Add)'),
            ('hrp_authorize_payroll', 'Can authorize payrolls'),
            ('hrp_view_payroll_reports', 'Can view payroll reports (Payroll -> Reports -> Summary, Bank, ...)'),

            ('hrp_view_system_reports', 'Can view system reports (System -> Reports -> User Activity, ...'),

            ('hrp_configure_appraisal', 'Can manage Appraisal settings [Administration > Appraisal]'),
            ('hrp_manage_appraisals', 'Can initiate and manage Appraisals'),

            ('hrp_manage_recruitment', 'Can manage vacancies and recruitment'),

            ('hrp_do_backup', 'Can do system administration: Backup, etc'),
        )

    CHOICES = (('S', 'Salaried'), ('C', 'Consultant'))
    GENDER_CHOICES = (('M', 'Male'), ('F', 'Female'))
    STATUS_CHOICES = (('A', 'Active'), ('R', 'Resigned'), ('T', 'Terminated'))
    MARITAL_STATUS_CHOICES = (
        ('S', 'Single'),
        ('M', 'Married'),
        ('D', 'Divorced')
    )
    CONTRACT_TYPE_CHOICES = (('P', 'Permanent'), ('C', 'Contract'), ('I', 'Internship'))
    user = models.OneToOneField(User, related_name='profile',
                null=True, blank=True)
    position = models.ForeignKey(Position)
    employee_type = models.CharField(
                    choices=CHOICES,
                    default=0,
                    max_length=16)
    service_line = models.ForeignKey(ServiceLine, null=True, blank=True,
        related_name="employee_profiles")
    branch = models.ForeignKey(Branch, null=True, blank=True)
    contract_type = models.CharField(max_length=2, choices=CONTRACT_TYPE_CHOICES, blank=False, default=MARITAL_STATUS_CHOICES[0])
    employed_on = models.DateTimeField(null=True, blank=True)
    title = models.ForeignKey(EmployeeTitle, null=True, blank=True)
    reports_to = models.ForeignKey('self', null=True, blank=True)
    gender = models.CharField(max_length=2, choices=GENDER_CHOICES, default=0)
    nssf_number = models.CharField(max_length=16, unique=True)
    bank = models.ForeignKey(BankBranch, null=False, blank=False)
    dependants = models.ForeignKey(Dependants, null=True, blank=True, default=0)
    bank_account_number = models.CharField(max_length=16, unique=True)
    tin_number = models.CharField(max_length=16, unique=True)
    deductions = models.ManyToManyField(DeductionType)
    allowances = models.ManyToManyField(AllowanceType)
    deleted_on = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(User, null=True, blank=True,
                    related_name='deleted_by')
    phone_number = models.CharField(max_length=16, blank=True)
    employee_number = models.CharField(max_length=16, blank=True)
    other_names = models.CharField(max_length=16, blank=True)
    number_of_children = models.CharField(max_length=3, blank=True)
    nin = models.CharField(max_length=12, blank=True)
    national_id_expiry = models.DateTimeField(null=22, blank=True)
    passport_number = models.CharField(max_length=22, blank=True)
    passport_expiry_date = models.DateTimeField(null=True, blank=True)
    driving_license = models.CharField(max_length=12, blank=True)
    license_expiry_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default=0)
    status_comment = models.TextField(blank=True)
#    roles = models.ManyToManyField(Group, blank=True, related_name='profiles')
    next_of_kin = models.ForeignKey(NextOfKin, blank=True)
    date_of_birth = models.DateTimeField()
    marital_status = models.CharField(max_length=2,
        choices=MARITAL_STATUS_CHOICES, default=MARITAL_STATUS_CHOICES[0])
    nationality = models.ForeignKey(Nationality, null=True)

    education_level = models.ForeignKey(EducationLevel, null=True, blank=True)
    skills = models.ManyToManyField(Skill, blank=True)
    memberships = models.ManyToManyField(Membership, blank=True)
    certifications = models.ManyToManyField(Certification, blank=True)
    education_level_remarks = models.TextField(blank=True)
    photo = models.FileField(upload_to=profile_photo_upload_directory, null=True, blank=True)

    def get_recurring_allowances(self):
        allowances = self.recurring_adjustments.filter(
            adjustment_type=1,
            allowance__isnull=False,
            expired_at__date__gte=timezone.now().date()
        )
        return allowances

    def get_recurring_deductions(self):
        deductions = self.recurring_adjustments.filter(
            adjustment_type=2,
            deduction__isnull=False,
            expired_at__date__gte=timezone.now().date()
        )
        return deductions


    def get_appraisals(self, **kwargs):
        status = kwargs.get('status', 'all')
        statuses = {
            'completed': '0',
            'pending': '1',
            'canceled': '2',
            'in_progress': '3',
            'ongoing': '1,3'
        }

        if status in statuses.keys():
            query = Q(status__in=statuses[status].split(','))
        else:
            query = Q()

        appraisals = self.appraisals.filter(query).order_by('-status')
        arr = []
        for appraisal in appraisals:
            if appraisal.flows.exists():
                arr.append(appraisal.id)
        return appraisals.filter(pk__in=arr)

    def get_received_appraisals(self, **kwargs):
        status = kwargs.get('status')
        q = Q()
        if status == 'ongoing':
            q = Q(employee_appraisal__status__in=['3',])
        # An earlier version of pg couldn't do this below
        #submission_ids = [i['id'] for i in self.appraisal_receipts.filter(q
        #    ).values('employee_appraisal', 'id').annotate(pk=models.Max('id'))]
        submissions = {}
        for i in self.appraisal_receipts.filter(q).values('employee_appraisal', 'id').order_by('id'):
            submissions[str(i['employee_appraisal'])] = i['id']
        submission_ids = submissions.values()

        received_appraisals = []
        for submission in self.appraisal_receipts.order_by('-employee_appraisal__status').filter(pk__in=submission_ids):
            appraisal = submission.employee_appraisal
            if appraisal.flows.count() > 1:
                f = appraisal.flows.order_by('-id')[0]
                if f.to_reviewer == self:
                    received_appraisals.append(submission.employee_appraisal)
        return received_appraisals

    def get_salary_scale(self):
        salary = self.get_contractual_pay()
        scale = SalaryScale.objects.get_scale(salary.amount)
        if scale:
            return scale
        else:
            return None
#        except SalaryScale.DoesNotExist:
#            return None
#        except SalaryScale.MultipleRecordsReturned:
#            return scale[]
#        return scale

    def get_fullname(self):
        return "%s %s %s %s" % (
            self.title if self.title else '',
            self.user.last_name,
            self.user.first_name if self.user.first_name else '',
            self.other_names if self.other_names else ''
        )

    def get_contractual_pay(self):
        try:
            cp = ContractualPay.objects.filter(employee=self.user
            ).order_by('-effective_since')[0]
        except:
            cp = ContractualPay(employee=self.user, amount=0).save()
        return cp

    def get_status(self):
        return self.get_status_display()
#        return self.STATUS_CHOICES[int(self.status)][1] #self.status

    def get_leave_approval(self):
        status = kwargs.get('status', 'all')
        statuses = {
            'completed': '0',
            'pending': '1',
            'canceled': '2',
            'in_progress': '3',
            'ongoing': '1,3'
        }

        return self.get_leave_approval_display()

    def get_contract_type(self):
        return self.get_contract_type_display()

    @staticmethod
    def get_queryset(params):
        pass

    def delete(self):
        import time
        import datetime
        profile = EmployeeProfile.objects.get(pk=self.id)
        profile.deleted_on = datetime.datetime.now()
        profile.save()
        profile.user.payslip_set.filter(payroll__authorized_by__isnull=True).delete()
#        super(EmployeeProfile, self).save(self)

    def add_to_unauthorized_payrolls(self):
        for payroll in Payroll.objects.filter(
                            authorized_by__isnull=True
                        ).exclude(
                            payslip__employee=self.user,
                            payslip__employee__is_active=False):
            c_pay = self.get_contractual_pay()
            payslip = Payslip(
                payroll = payroll,
                employee = self.user,
                contractual_pay = c_pay,
                contractual_pay_amount = c_pay.amount
            )
            payslip.save()

#            Generate and save figures for quicker access
            payslip.update_values()

            for allowance in self.allowances.all():
                PayslipAllowance(
                    payslip=payslip,
                    allowance_type=allowance,
                    amount=0,
                    comment=None
                ).save()

#    def remove_from_unauthorized_payrolls(self):
#        for payroll in Payroll.objects.filter(authorized_by__isnull=True,
#            payslip__employee=self.user):

    def update_unauthorized_payslips(self):
        for slip in Payslip.objects.filter(
            payroll__authorized_by__isnull=True, employee=self.user):
            if self.status != 'A': # Terminated/Resigned
                slip.delete()
            else:
                slip.update_values()

    def exists_in_payroll(self):
#        if self.user.payslip_set.filter(payroll__authorized_at__isnull=False).count():
        if self.user.payslip_set.filter(
            payroll__authorized_at__isnull=False).exits():
            return True
        return False

def upload_directory(instance, filename):
    return 'payroll/static/uploads/{}/{}'.format(
        instance.employee_profile.user.username, filename)

class EmployeeDocument(models.Model):
    employee_profile = models.ForeignKey(EmployeeProfile,
        related_name='documents')

    document = models.FileField(upload_to=upload_directory, null=True, blank=True)
    description = models.CharField(max_length=32, blank=True)

    def filename(self):
        import os
        return os.path.basename(self.document.name)
