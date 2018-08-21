import logging
from decimal import Decimal, ROUND_HALF_UP

from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import get_list_or_404

from .hrp_fields import CurrencyField

logger = logging.getLogger(__name__)

class AllowanceType(models.Model):
    class Meta:
        ordering = ['name']
    name = models.CharField(max_length=32, unique=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    is_asset_allowance = models.BooleanField(default=False)
    is_taxed = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class DeductionType(models.Model):
    class Meta:
        ordering = ['name']

    name = models.CharField(max_length=32, unique=True)
    affects_gross_pay = models.BooleanField()
    description = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name

class Currency(models.Model):
    name = models.CharField(max_length=32,
        unique=True)
    symbol = models.CharField(max_length=8)

    def __str__(self):
        return self.name

class ContractualPay(models.Model):
    employee = models.ForeignKey(User, null=True, blank=True)
    amount = models.DecimalField(max_digits=16, decimal_places=2, blank=False,)
    effective_since = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    currency = models.ForeignKey(Currency)

class Log(models.Model):
    time_stamp = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    user = models.ForeignKey(User, null=True, blank=True)
    session = models.CharField(null=True, blank=True, max_length=1024)
    action = models.CharField(null=True, blank=True, max_length=1024)

    def __str__(self):
        return action

class PayPeriod(models.Model):
    class Meta:
    	ordering = ['-id']
    start_date = models.DateField(null=False, blank=False)
    end_date = models.DateField(null=False, blank=False)
    total_working_days = models.DecimalField(max_digits=5, decimal_places=2)

    def get_payroll(self):
        if self.has_payroll():
            return self.payroll
            return self.payroll_set.all()[0]
        else:
            return None

    def has_payroll(self):
        try:
            p = self.payroll
        except Exception as e: #PayPeriod.RelatedObjectDoesNotExist as e:
            return False
        return bool(p)

    def has_payroll_old(self):
        return bool(self.payroll_set.all())

    def __str__(self):
        return '%s to %s' % (self.start_date.strftime("%d/%m/%Y"),
            self.end_date.strftime("%d/%m/%Y"))
        return '%s to %s' % (self.start_date.strftime("%d/%m/%Y"),
            self.end_date.strftime("%d %b %Y"))

class Payroll(models.Model):
    date = models.DateField(auto_now_add=True, null=True, blank=True)
    authorized_at = models.DateTimeField(null=True, blank=True)
    authorized_by = models.ForeignKey(User, null=True, blank=True)
    notified_recipients = models.BooleanField(default=False)
    pay_period = models.OneToOneField(PayPeriod)
    total_basic_pay = CurrencyField()
    total_allowances = CurrencyField()
    total_gross_pay = CurrencyField()
    total_employee_nssf = CurrencyField()
    total_msu_nssf = CurrencyField()
    total_paye = CurrencyField()
    total_deductions = CurrencyField()
    total_net_pay = CurrencyField()
    total_contractual_pay = CurrencyField()

    def __str__(self):
        return str(self.pay_period)

    def is_authorized(self):
        return True if self.authorized_by else False

    def get_number_of_employees(self):
        return self.payslip_set.all().count()

    def generate_payslips(self):

        payslips = []
        for user in User.objects.filter(is_active=True,
            profile__deleted_on__isnull=True, profile__status='A'):
            employee_profile = user.profile

            c_pay = employee_profile.get_contractual_pay()
            payslip = user.payslip_set.create(
                payroll = self,
                contractual_pay = c_pay,
                contractual_pay_amount = c_pay.amount
            )

            for allowance in employee_profile.get_recurring_allowances():
                payslip.allowances.create(
                    allowance_type=allowance.allowance,
                    amount=allowance.amount,
                    comment=allowance.comment
                )

            for deduction in employee_profile.get_recurring_deductions():
                payslip.deductions.create(
                    deduction_type=deduction.deduction,
                    amount=deduction.amount,
                    comment=deduction.comment
                )
#            Generate and save figures for quicker access
            payslip.update_values()

            payslips.append(payslip)

        return payslips

    def save_totals(self):
        self.total_allowances = self.get_total_allowances_t()
        self.total_gross_pay = self.get_total_contractual_pay_t()
        self.save()

    def __get_payslips(self, user):
        return Payslip.objects.filter(
                employee__in=EmployeeProfile.objects.all().values('user_id'), payroll=self
                    ) if user.has_perm('payroll.can_view_payroll') else \
                    Payslip.objects.filter(payroll=self, employee=user,
                    employee__in=EmployeeProfile.objects.all().values('user_id'))

    def get_total_contractual_pay(self, user):
        total_contractual_pay = 0

        for payslip in self.__get_payslips(user): #self.payslip_set.all():
            total_contractual_pay = total_contractual_pay + \
                int(payslip.employee.profile.get_contractual_pay().amount)

        return total_contractual_pay

    def get_total_net_pay(self, user):
    #    return self.payslip_set.all().aggregate(Sum('net_pay'))['net_pay']
        total_net_pay = 0
        for payslip in self.__get_payslips(user):
            total_net_pay = total_net_pay + \
                Decimal(str(payslip.get_net_pay())).quantize(Decimal('0.00'), ROUND_HALF_UP)

        return total_net_pay

    def get_total_basic_pay(self, user):

        total_basic_pay = 0
        for payslip in self.__get_payslips(user):
            total_basic_pay = total_basic_pay + \
                Decimal(str(payslip.get_basic_pay())).quantize(Decimal('0.00'), ROUND_HALF_UP)
        return total_basic_pay

    def get_total_gross_pay(self, user):
     #   return self.payslip_set.all().aggregate(Sum('gross_pay'))['gross_pay']
        total_gross_pay = 0
        for payslip in self.__get_payslips(user):
            total_gross_pay = total_gross_pay + \
                Decimal(str(payslip.get_gross_pay())).quantize(Decimal('0.00'), ROUND_HALF_UP)
        return total_gross_pay

    def get_total_employee_nssf(self, user):

        total_employee_nssf = 0
        for payslip in self.__get_payslips(user):
            total_employee_nssf = total_employee_nssf + \
                Decimal(str(payslip.get_employee_nssf())).quantize(Decimal('0.00'), ROUND_HALF_UP)
        return total_employee_nssf

    def get_total_msu_nssf(self, user):

        total_msu_nssf = 0
        for payslip in self.__get_payslips(user):
            total_msu_nssf = total_msu_nssf + \
                Decimal(str(payslip.get_msu_nssf())).quantize(Decimal('0.00'), ROUND_HALF_UP)
        return total_msu_nssf

    def get_total_paye(self, user):

        total_paye = 0
        for payslip in self.__get_payslips(user):
            total_paye = total_paye + Decimal(str(payslip.get_paye()
                )).quantize(Decimal('0.00'), ROUND_HALF_UP)
        return total_paye

    def get_total_allowances(self, user):

        total_allowances = 0
        for payslip in self.__get_payslips(user):
            total_allowances = total_allowances + \
                Decimal(str(payslip.get_total_allowances())).quantize(Decimal('0.00'), ROUND_HALF_UP)
        return total_allowances

    def get_total_deductions(self, user):

        total_deductions = 0
        for payslip in self.__get_payslips(user):
            total_deductions = total_deductions + \
                Decimal(str(payslip.get_other_deductions())).quantize(Decimal('0.00'), ROUND_HALF_UP)
        return total_deductions

#    def get_total_outreach_allowance(self, user):
#
#        total_outreach_allowance = 0
#        for payslip in self.__get_payslips(user):
#            total_outreach_allowance = total_outreach_allowance + payslip.get_outreach_allowance()
#        return total_outreach_allowance

    def get_total_contractual_pay1(self):
        total_contractual_pay = 0

        payslip_list = get_list_or_404(Payslip, payroll=self)
#                ) if user.has_perm('payroll.can_view_payroll') else \
#                get_list_or_404(Payslip, payroll=self, employee=self.use)

        for payslip in payslip_list: #self.payslip_set.all():
            total_contractual_pay = total_contractual_pay + \
                int(payslip.employee.profile.get_contractual_pay().amount)

        return total_contractual_pay

######### for summary report in template (no arguments) #######
####
    def get_total_contractual_pay_t(self):
        total_contractual_pay = 0

        payslip_list = get_list_or_404(Payslip, payroll=self)

        for payslip in payslip_list: #self.payslip_set.all():
            total_contractual_pay = total_contractual_pay + \
                int(payslip.employee.profile.get_contractual_pay().amount)

        return total_contractual_pay

    def get_total_net_pay_t(self):
        payslip_list = get_list_or_404(Payslip, payroll=self) \

        total_net_pay = 0
        for payslip in payslip_list:
            total_net_pay = total_net_pay + \
                Decimal(str(payslip.get_net_pay())).quantize(Decimal('0.00'), ROUND_HALF_UP)

        return total_net_pay

    def get_total_basic_pay_t(self):
        payslip_list = get_list_or_404(Payslip, payroll=self)

        total_basic_pay = 0
        for payslip in payslip_list:
            total_basic_pay = total_basic_pay + \
                Decimal(str(payslip.get_basic_pay())).quantize(Decimal('0.00'), ROUND_HALF_UP)
        return total_basic_pay

    def get_total_gross_pay_t(self):
        payslip_list = get_list_or_404(Payslip, payroll=self)

        total_gross_pay = 0
        for payslip in payslip_list:
            total_gross_pay = total_gross_pay + \
                Decimal(str(payslip.get_gross_pay())).quantize(Decimal('0.00'), ROUND_HALF_UP)
        return total_gross_pay

    def get_total_employee_nssf_t(self):
        payslip_list = get_list_or_404(Payslip, payroll=self)

        total_employee_nssf = 0
        for payslip in payslip_list:
            total_employee_nssf = total_employee_nssf + \
                Decimal(str(payslip.get_employee_nssf())).quantize(Decimal('0.00'), ROUND_HALF_UP)
        return total_employee_nssf

    def get_total_msu_nssf_t(self):
        payslip_list = get_list_or_404(Payslip, payroll=self)

        total_msu_nssf = 0
        for payslip in payslip_list:
            total_msu_nssf = total_msu_nssf + \
                Decimal(str(payslip.get_msu_nssf())).quantize(Decimal('0.00'), ROUND_HALF_UP)
        return total_msu_nssf

    def get_total_paye_t(self):
        payslip_list = get_list_or_404(Payslip, payroll=self)

        total_paye = 0
        for payslip in payslip_list:
            total_paye = total_paye + Decimal(str(payslip.get_paye()
                )).quantize(Decimal('0'), ROUND_HALF_UP)
        return total_paye

    def get_total_allowances_t(self):
        payslip_list = get_list_or_404(Payslip, payroll=self)

        total_allowances = 0
        for payslip in payslip_list:
            total_allowances = total_allowances + \
                Decimal(str(payslip.get_total_allowances())).quantize(Decimal('0.00'), ROUND_HALF_UP)
        return total_allowances

    def get_total_deductions_t(self):
        payslip_list = get_list_or_404(Payslip, payroll=self)

        total_deductions = 0
        for payslip in payslip_list:
            total_deductions = total_deductions + \
                Decimal(str(payslip.get_other_deductions())).quantize(Decimal('0.00'), ROUND_HALF_UP)
        return total_deductions

#    def get_total_outreach_allowance_t(self):
#        payslip_list = get_list_or_404(Payslip, payroll=self)
#
#        total_outreach_allowance = 0
#        for payslip in payslip_list:
#            total_outreach_allowance = total_outreach_allowance + payslip.get_outreach_allowance()
#        return total_outreach_allowance

#    def save(self, *args, **kwargs):
#        new = True
#        if self.id:
#            new = False
#
#        super(Payroll, self).save(*args, **kwargs)
#
#        if new:
#            self.generate_payslips()

class Payslip(models.Model):
    payroll = models.ForeignKey(Payroll)
    employee = models.ForeignKey(User)
    contractual_pay = models.ForeignKey(ContractualPay)
    nssf = CurrencyField()
    paye = CurrencyField()
    msu_nssf = CurrencyField()
    advance = CurrencyField()
    net_pay = CurrencyField()
    total_allowances = CurrencyField()
    total_deduction = CurrencyField()
    gross_pay = CurrencyField()
    taxable_income = CurrencyField()
#    allowances = models.ManyToManyField(AllowanceType,
#        through='PayslipAllowance')
#    deductions = models.ManyToManyField(DeductionType,
#        through='PayslipDeduction')
    total_days_worked = models.DecimalField(max_digits=4, decimal_places=1,
        default=Decimal('-1'))
#    total_outreach_days = models.DecimalField(max_digits=4, decimal_places=1,
#        default=Decimal('0.0'))
    contractual_pay_amount = CurrencyField()
    basic_pay = CurrencyField()
#    outreach_allowance = CurrencyField()
#    funds_source = models.ManyToManyField("DonorLine",
#                        through="PayslipFundsSource",
#                        related_name="funds_source_set",
#                        max_length=16)

    def update_values(self):
        payslip = self
        payslip.total_days_worked = payslip.get_total_days_worked()
        payslip.save()
        payslip.contractual_pay_amount = payslip.employee.profile.get_contractual_pay().amount
        payslip.save()
        basic_pay = payslip.get_basic_pay()
        payslip.basic_pay = basic_pay #payslip.get_basic_pay()
        payslip.save()
        payslip.total_allowances = payslip.get_total_allowances()
        payslip.save()
        payslip.total_deduction = payslip.get_other_deductions()
        payslip.save()
        payslip.gross_pay = payslip.get_gross_pay()
        payslip.save()
        payslip.nssf = payslip.get_employee_nssf()
        payslip.save()
        payslip.msu_nssf = payslip.get_msu_nssf()
        payslip.save()
        payslip.paye = payslip.get_paye()
        payslip.save()
        payslip.net_pay = payslip.get_net_pay()
        payslip.save()

        return payslip

    def get_total_allowances(self):

        q = self.allowances.filter(
                allowance_type__is_asset_allowance=False
            ).aggregate(total_amount=models.Sum('amount'))
        return float(q['total_amount']) if q['total_amount'] else 0

        total = 0.0
        for allowance in self.allowances.filter(
            allowance_type__is_asset_allowance=False):
            total = total + allowance.amount
        return total

    def get_gratuity(self):
        """Returns the total of the previous three months basic pay"""
        payslips = Payslip.objects.filter(employee=self.employee).order_by(
                    '-id')[:3]

        gratuity = 0
        for slip in payslips:
            gratuity = gratuity + slip.get_basic_pay()

        return gratuity

    def get_other_deductions(self):
        q = self.deductions.exclude(deduction_type__affects_gross_pay=True
            ).aggregate(total_amount=models.Sum('amount'))
        return float(q['total_amount']) if q['total_amount'] else 0

    def get_basic_pay(self):
        contractual_pay = float(self.employee.profile.get_contractual_pay(
                            ).amount)
        total_days_worked = float(self.get_total_days_worked())
        payroll_days = float(self.payroll.pay_period.total_working_days)

        if Decimal(str(total_days_worked)).quantize(Decimal('0.00'), ROUND_HALF_UP) != Decimal('0.00'):
            basic_pay = contractual_pay * (float(str(total_days_worked))/payroll_days)
        else:
            basic_pay = 0

        return basic_pay


    def get_local_govt_tax(self):
#        Deduct local government tax
        q = self.deductions.filter(deduction_type__affects_gross_pay=True
            ).aggregate(tax=models.Sum('amount'))
        tax = float(q['tax']) if q['tax'] else 0
        return tax

    def get_gross_pay(self):
        contractual_pay = float(self.employee.profile.get_contractual_pay(
                            ).amount)
        total_days_worked = float(self.get_total_days_worked())
        payroll_days = float(self.payroll.pay_period.total_working_days)

        gross_pay = contractual_pay * (float(total_days_worked)/payroll_days
            ) + int(self.get_total_allowances())

        return gross_pay

    def get_paye(self):

        gross_pay = self.get_gross_pay() - self.get_local_govt_tax()
        paye = 0

        if gross_pay >= 10000000:
            paye = (gross_pay - 10000000)*0.4 + 2902000
        elif gross_pay >= 410000:
            paye = (gross_pay - 410000)*0.3 + 25000
        elif gross_pay >= 335000:
            paye = (gross_pay - 335000)*0.2 + 10000
        elif gross_pay >= 235000:
            paye = (gross_pay - 235000)*0.1
        return paye


    def get_employee_nssf(self):
        # get nssf if chap pays it
        gross_pay = self.get_gross_pay()

        return gross_pay * 0.05

    def get_msu_nssf(self):
        # get nssf if chap pays it

#        if self.deductions.filter(employeeprofile__name__iexact='NSSF').exists():
        gross_pay = self.get_gross_pay()
        msu_nssf = gross_pay * 0.1
#        else:
#            msu_nssf = 0
        return msu_nssf

    def get_total_non_taxable_allowances(self):
        amount = self.allowances.filter(allowance_type__is_taxed=False
            ).aggregate(amount=models.Sum('amount'))['amount']
        return float(amount if amount is not None else 0)

    def get_net_pay(self):
        net_pay = self.get_gross_pay() - self.get_total_deductions(
            ) - self.get_local_govt_tax()

        return net_pay + self.get_total_non_taxable_allowances()

    def get_total_deductions(self):
        return self.get_employee_nssf() + \
             self.get_paye() + self.get_other_deductions()
        return self.get_advance() + self.get_employee_nssf() + \
            self.get_msu_nssf() + self.get_paye() + self.get_other_deductions()

    def get_total_days_worked(self):
        if self.total_days_worked == -1: # -1 is default
            return float(self.payroll.pay_period.total_working_days)
        else:
            return float(self.total_days_worked)

class PayslipDeduction(models.Model):
    payslip = models.ForeignKey(Payslip, related_name='deductions')
    deduction_type = models.ForeignKey(DeductionType)
    amount = models.DecimalField(max_digits=16, decimal_places=2, blank=False)
    comment = models.CharField(max_length=512, null=True, blank=True)

class PayslipAllowance(models.Model):
    payslip = models.ForeignKey(Payslip, related_name='allowances')
    allowance_type = models.ForeignKey(AllowanceType)
    amount = models.DecimalField(max_digits=16, decimal_places=2, blank=False,)
    comment = models.CharField(max_length=512, null=True, blank=True)
