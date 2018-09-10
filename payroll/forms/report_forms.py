__author__ = "Steven Kawuma <kawuma@gmail.com>"
__date__ = "Jan 4, 2017 6:24:09 PM"

from django.forms import *
from django.contrib.auth.models import User
from payroll.models import PayPeriod, ContractualPay, EmployeeProfile
from payroll.models import Bank, ServiceLine, Position

from .hrp_fields import UserModelChoiceField, EmployeeModelChoiceField
from .hrp_widgets import JQueryUIDatepickerWidget, DivErrorList

class EmployeeSearchForm(Form):

    service_line_field = BooleanField(required=False)
    position_field = BooleanField(required=False)
    service_line_field = BooleanField(required=False)
    nssf_number_field = BooleanField(required=False)
    bank_field = BooleanField(widget=CheckboxInput(attrs={'value': 1}),required=False)
    acct_no_field = BooleanField(required=False)
    tin_field = BooleanField(required=False)
    salary_field = BooleanField(required=False)
    status_field = BooleanField(required=False)
    employee_number_field = BooleanField(required=False)
    email_field = BooleanField(required=False)
    phone_number_field = BooleanField(required=False)
    sort_code_field = BooleanField(required=False)

    position = ModelChoiceField(queryset=Position.objects.all(),
                    empty_label='--Any--', required=False)
    service_line = ModelChoiceField(queryset=ServiceLine.objects.all(),
                    empty_label='--Any--', required=False)
    bank = ModelChoiceField(queryset=Bank.objects.all(),
                    empty_label='--Any--', required=False)

class UserActivitySearchForm(Form):
    user = UserModelChoiceField(required=False,
            queryset=User.objects.all().order_by('last_name'),
            empty_label='-- All --')
    start_date = CharField(required=False, min_length=10,
                    widget=JQueryUIDatepickerWidget)
    end_date = CharField(required=False, min_length=10,
                    widget=JQueryUIDatepickerWidget)
    def clean(self):
        data = self.cleaned_data
        if data['start_date'] and data['end_date'] and (data['end_date'] < data['start_date']):
            msg = 'The FROM date cannot be greater than the TO date.'
            raise ValidationError(msg)
        return data

class PayrollSummaryReportForm(Form):
    pay_period = ModelChoiceField(
                    queryset=PayPeriod.objects.filter(
                    payroll__authorized_at__isnull=False),
                    required=False,
                    empty_label='-- All --')
                    
class PayperiodSearchForm(Form):
    def __init__(self, *args, **kwargs):
        self.error_class = DivErrorList
        super(PayperiodSearchForm, self).__init__(*args, **kwargs)

    start_date = CharField(required=False, min_length=10, widget=JQueryUIDatepickerWidget)
    end_date = CharField(required=False, min_length=10, widget=JQueryUIDatepickerWidget)
    pay_period = ModelChoiceField(queryset=PayPeriod.objects.filter(
                        payroll__authorized_at__isnull=False),
                    required=False,
                    empty_label='-- All --')
    service_line = ModelChoiceField(queryset=ServiceLine.objects.all(),
                    required=False,
                    empty_label='-- All --')
    
    number_of_staff = BooleanField(required=False)
    total_contractual_pay = BooleanField(required=False)
    total_allowances = BooleanField(required=False)
    total_deductions = BooleanField(required=False)
    total_paye = BooleanField(required=False)
    total_nssf = BooleanField(required=False)
    total_msu_nssf = BooleanField(required=False)
    total_net_pay = BooleanField(required=False)
    authorized_by = BooleanField(required=False)
    authorized_at = BooleanField(required=False)
    total_outreach_allowance = BooleanField(required=False)
    total_gross_pay = BooleanField(required=False)
#    widgets = {
#        'start_date': TextInput(required=False)
#    }

class ContractualPayForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(ContractualPayForm, self).__init__(*args, **kwargs)
        self.error_class = DivErrorList

    CHOICES = (('0', 'Salaried'), ('1', 'Consultant'))

#    employee = IntegerField(widget=HiddenInput, required=False)

    class Meta:
        model = ContractualPay
        exclude = ('effective_since',)
        widgets = {
            'amount': TextInput(attrs={'text-align': 'right'})
        }

class SalaryHistoryForm(Form):
    def __init__(self, *args, **kwargs):
        super(SalaryHistoryForm, self).__init__(*args, **kwargs)
        self.error_class = DivErrorList

    employee = EmployeeModelChoiceField(required=True,
                    queryset=EmployeeProfile.objects.order_by('user__last_name'
                    ),
                    empty_label='-- Select --',
                    error_messages={'required': "Select an employee to search for."})
    start_date = CharField(required=False, min_length=10,
                    widget=JQueryUIDatepickerWidget)
    end_date = CharField(required=False, min_length=10,
                    widget=JQueryUIDatepickerWidget)

