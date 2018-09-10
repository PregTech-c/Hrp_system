__author__ = "Steven Kawuma <kawuma@gmail.com>"
__date__ = "Jan 4, 2017 6:37:48 PM"

import datetime

from payroll.models import AllowanceType, PayPeriod, Payslip, PayslipAllowance
from payroll.models import DeductionType, Payroll, Bank, ServiceLine
from payroll.models import PayslipDeduction, ServiceLine, EmployeeRecurringAdjustment
from payroll.models.employee_models import EmployeeProfile

from django.forms import *
from .hrp_widgets import JQueryUIDatepickerWidget, DivErrorList
from .hrp_fields import EmployeeModelChoiceField

class PayslipSearchForm(Form):
    emp_name = CharField(max_length=10, required=False)
#    service_line = ModelChoiceField(queryset=ServiceLine.objects.all(), 
#        empty_label='-- All --')

class PayPeriodForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(PayPeriodForm, self).__init__(*args, **kwargs)
        self.error_class = DivErrorList
        self.fields['start_date'].min_length = 20
        self.fields['end_date'].min_length = 20

#    start_date = CharField(min_length=10, widget=JQueryUIDatepickerWidget())
#    end_date = CharField(min_length=10, widget=JQueryUIDatepickerWidget())
    class Meta:
        model = PayPeriod
        exclude = ()
        widgets = {
            'payroll_generated': HiddenInput,
            'payroll': HiddenInput,
            'start_date': JQueryUIDatepickerWidget,
#            'start_date': DateInput(attrs={'class': 'dateinput'}),
            'end_date': JQueryUIDatepickerWidget,
#            'end_date': DateInput(format='%m/%d/%Y', attrs={'class': 'dateinput'})
        }

    def clean(self):
        cleaned_data = self.cleaned_data

        if cleaned_data.get('start_date') is None or \
            cleaned_data.get('end_date') is None:
            raise ValidationError('Enter both start and end dates.')
            return cleaned_data

        if cleaned_data['start_date'] > cleaned_data['end_date']:
            msg = 'Start date should not come after the end date.'
#            self._errors['start_date'] = DivErrorList([msg])
            raise ValidationError(msg)
#            del cleaned_data['start_date']
#            del cleaned_data['end_date']

        if not self.instance:
            try:
                period = PayPeriod.objects.get(
                            start_date__exact=cleaned_data['start_date'],
                            end_date__exact=cleaned_data['end_date'])
                msg = 'Pay period already exists.'
                raise ValidationError(msg)
            except PayPeriod.DoesNotExist:
                pass

        return cleaned_data


#    def clean_end_date(self):
#        end_date = self.cleaned_data.get('end_date')
#
#        if end_date:
#            try:
#                end_date = datetime.datetime.strptime(end_date, '%d/%m/%Y')
#            except ValueError:
#                end_date = None
#                self._errors['end_date'] = 'Invalid date'
#            return end_date

#    def clean_start_date(self):
#        start_date = self.cleaned_data.get('start_date')
#
#        if start_date:
#            try:
#                start_date = datetime.datetime.strptime(start_date, '%d/%m/%Y')
#            except ValueError:
#                start_date = None
#                self._errors['start_date'] = 'Invalid date'
#            return start_d

class PayslipAllowanceForm(ModelForm):

    allowance_type = ModelChoiceField(queryset=AllowanceType.objects.all(
                        ).order_by('name'), empty_label=None)
    class Meta:
        model = PayslipAllowance
        exclude = ()
        widgets = {
            'payslip': HiddenInput,
            'comment': Textarea(attrs={'cols': 35, 'rows': 3})
        }

#    def clean_amount(self):
#        cleaned_data = self.cleaned_data['amount']
#        try:
#            data=int(self.cleaned_data['amount'])
#        except:
#            raise ValidationError('Enter a valid amount')
#        self._errors['amount'] = DivErrorList(['Enter a valid amount'])
#        del self.cleaned_data['amount']
#
#        return cleaned_data
#
#    def save(self, ):
#
#        try:
#            type = self.data['allowance_type']
#            allowance = PayslipAllowance.objects.get(
#                payslip=self.fields['payslip'],
#                allowance_type=1
#                # self.fields['allowance_type'].
#            )
#
#            PayslipAllowance(
#                pk=allowance.id,
#                amount=self.fields['amount'],
#                comment=self.fields['comment']).save()
#        except PayslipAllowance.DoesNotExist:
#
#            super(PayslipAllowanceForm, self).save()

class PayslipDeductionForm(ModelForm):

    deduction_type = ModelChoiceField(queryset=DeductionType.objects.all(
                        ).order_by('name'), empty_label=None)
    class Meta:
        model = PayslipDeduction
        exclude = ()
        widgets = {
            'payslip': HiddenInput,
            'comment': Textarea(attrs={'cols': 30, 'rows': 3})
        }

class PayslipTotalDaysWorked(ModelForm):

#    total_days_worked = CharField()
    class Meta:
        model = Payslip
        fields = ('id', 'total_days_worked')
        widgets = {
            'payslip': HiddenInput,

        }

    def clean_total_days_worked(self):
        try:
            data = float(self.cleaned_data['total_days_worked'])
        except:
            raise ValidationError('Invalid entry %s for days worked' % self.cleaned_data['total_days_worked'])
        return data

class SearchPayrollForm(Form):
    def __init__(self, *args, **kwargs):
        super(SearchPayrollForm, self).__init__(*args, **kwargs)
        self.error_class = DivErrorList

    payroll = ModelChoiceField(
                    queryset=Payroll.objects.filter(
                        authorized_at__isnull=False
                    ).order_by('-id'),
                    empty_label='-- Select --')
    department = ModelChoiceField(
                    queryset=ServiceLine.objects.all(),
                    required=False,
                    empty_label='-- All --')
    bank = ModelChoiceField(
            queryset=Bank.objects.all().order_by('name'),
            required=False,
            empty_label='-- All --')

    categorize = BooleanField(required=False,widget=CheckboxInput)

class RecurringAdjustmentForm(ModelForm):
    def __init__(self, *args, **kwargs):
        adj_type = kwargs.pop('adj_type')
        super(RecurringAdjustmentForm, self).__init__(*args, **kwargs)
        
        self.fields['adjustment_type'].initial = adj_type
        
#        if not self.instance.id:
        if str(adj_type) == '1':
            del self.fields['deduction']
            self.fields['allowance'].empty_label = '-- Select --'
            self.fields['allowance'].required = True
        else:
            del self.fields['allowance']
            self.fields['deduction'].empty_label = '-- Select --'
            self.fields['deduction'].required = True

    class Meta:
        model = EmployeeRecurringAdjustment
        exclude = ()
        widgets = {
            'adjustment_type': HiddenInput,
            'comment': Textarea(attrs={'rows': 4}),
            'expired_at': JQueryUIDatepickerWidget
        }
    employee = EmployeeModelChoiceField(queryset=EmployeeProfile.objects.all(),
        empty_label=None)
    
    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if int(amount) <= 0:
            raise ValidationError("Please enter an amount '%(amount)s'",
                params=dict(amount=self.cleaned_data['allowance'])
            )
        return amount
    
    def clean(self):
        profile = self.cleaned_data['employee']
        if self.cleaned_data.get('deduction'):
            if profile.recurring_adjustments.filter(adjustment_type=2,
                expired_at__gte=datetime.datetime.now().date()) and \
                    not self.instance.id:
                raise ValidationError(
                    'Recurring deduction already exists for %(name)s',
                     params={'name': profile.get_fullname()}
                )
        elif self.cleaned_data.get('allowance'):
            if profile.recurring_adjustments.filter(adjustment_type=1,
                expired_at__gte=datetime.datetime.now().date()) and \
                    not self.instance.id:
                raise ValidationError(
                    'Recurring allowance already exists for %(name)s',
                     params={'name': profile.get_fullname()}
                )
        return self.cleaned_data

class RecurringAdjustmentSearchForm(Form):
    name = CharField(required=False)
    adjustment_type = ChoiceField(
        choices=((0, '-- All --'),) + EmployeeRecurringAdjustment.TYPES)
#    employee = UserModelChoiceField(
#        empty_label='-- All --',
#        required=False)
#    issue_status = forms.ChoiceField(
#        choices=(
#            (0, '-- Any --'), 
#            (1, 'Issued'), 
#            (2, 'Available')
#            )
#        )
