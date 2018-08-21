__author__ = "Steven Kawuma <kawuma@gmail.com>"
__date__ = "Dec 14, 2016 9:00:52 PM"

from django.contrib.auth.models import User, Permission
from django.conf import settings
from django.forms import ModelForm, ValidationError

from django.forms import *
from payroll.models import *
from .hrp_widgets import DivErrorList

class DeductionTypeForm(ModelForm):
    class Meta:
        exclude = ()
        model = DeductionType
        widgets = {
            'name': TextInput(attrs={'size': '30'}),
            'description': TextInput(attrs={'size': '60'}),
        }

class AllowanceTypeForm(ModelForm):
    class Meta:

        model = AllowanceType
        exclude = ()
        widgets = {
            'name': TextInput(attrs={'size': '30'}),
            'description': TextInput(attrs={'size': '60'}),
        }

class ServiceLineForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ServiceLineForm, self).__init__(*args, **kwargs)
        self.fields['service_line_type'].empty_label = None
        self.fields['parent_service_line'].empty_label = 'None'
        self.error_class = DivErrorList 

    class Meta:
        model = ServiceLine
        exclude = ()
        widgets = {
            'name': TextInput(attrs={'size': '30'}),
        }

class ServiceLineTypeForm(ModelForm):

    class Meta:
        model = ServiceLineType
        exclude = ()
        widgets = {
            'name': TextInput(attrs={'size': '60'}),
        }

class BankForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(BankForm, self).__init__(*args, **kwargs)
        self.error_class = DivErrorList

    class Meta:
        model = Bank
        exclude = ()
        widgets = {
            'name': TextInput(attrs={'size': '60'}),
        }

    def clean(self):
        data = self.cleaned_data

        q = Bank.objects.filter(name=data['name'])
        if self.instance.pk:
            q = q.exclude(pk=self.instance.pk)

        if q:
            msg = "%s bank already exists." % data['name']
            raise ValidationError(msg)
        return data

class BankBranchForm(ModelForm):
    class Meta:
        model = BankBranch
        exclude = ()
        widgets = {
            'bank': HiddenInput,
            'branch_name': TextInput(attrs={'size': '60'}),
            'phone_number': TextInput(attrs={'size': '30'}),
            'sort_code': TextInput(attrs={'size': '30'})
        }

    def clean(self):
        data = self.cleaned_data

        q = BankBranch.objects.filter(bank=data['bank'],
                        branch_name__iexact=data['branch_name'])
        if self.instance.pk:
            q = q.exclude(pk=self.instance.pk)

        if q:
            msg = "%s already exists as a branch name for this bank" % data['branch_name']
            raise ValidationError(msg)
        return data

class SalaryScaleForm(ModelForm):
    class Meta:
        model = SalaryScale
        exclude = ()
    def clean_range_from(self):
        data = self.cleaned_data['range_from']
        if data:
            try:
                data = float(str(data))
            except:
                self._errors['range_from'] = DivErrorList(['Enter only figures'])
        return data

    def clean_range_to(self):
        data = self.cleaned_data['range_to']
        if data:
            try:
                data = float(str(data))
            except:
                self._errors['range_to'] = DivErrorList(['Enter only figures'])
        return data

    def clean(self):
        data = self.cleaned_data
        range_from = data.get('range_from')
        range_to = data.get('range_to')

        if not range_from and not range_to:
            raise ValidationError('Both FROM and TO figures may not be empty.')

        if range_to and (range_from > range_to):
            raise ValidationError('The FROM figure cannot be greater than the TO figure.')

        if self.instance.id:
            edit = True
        else:
            edit = False

        if range_from:
            scale = SalaryScale.objects.get_scale(range_from)
            if scale:
                if not edit or (edit and scale.id != self.instance.id):
                    raise ValidationError('The FROM figure is within the %s scale range.' % (
                    scale.__str__().upper(),))
        if range_to:
            scale = SalaryScale.objects.get_scale(range_to)
            if scale:
                if not edit or (edit and scale.id != self.instance.id):
                    raise ValidationError('The TO figure is within the %s scale range.' % (
                    scale.__str__().upper(),))
#
#        exists = SalaryScale.objects.filter(range_to__gte=range_from,
#                    range_from__lte=range_from)
#        if exists:
#            raise ValidationError('The from figure is within the %s scale range.' % (
#                    exists[0].code,))
#
#        exists = SalaryScale.objects.filter(range_to__gte=range_to,
#                    range_from__lte=range_to)
#        if exists:
#            raise ValidationError('The TO figure is within the %s scale range.' % (
#                    exists[0].code,))
        return data

class AuthorizePayrollEmailList(ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s (%s) - %s" % (obj.get_profile().get_fullname(),
                    obj.userprofile.position,
                    obj.email
                )
class SendEmailForm(Form):


    def __init__(self, user, *args, **kwargs):
        super(SendEmailForm, self).__init__(*args, **kwargs)
        self.error_class = DivErrorList
        self.user=user
        self.fields['recipient'].queryset=User.objects.filter(
            Q(user_permissions=Permission.objects.get(codename='hrp_authorize_payroll'))|
            Q(groups__permissions=Permission.objects.get(codename='hrp_authorize_payroll'))|
            Q(is_superuser=True)
        ).exclude(id=self.user.id)
        self.fields['recipient'].empty_lable = None

    recipient = AuthorizePayrollEmailList(
        queryset=User.objects.all(),
        empty_label=None
    )
    text = CharField(required=True, widget=Textarea)

    def send_email(self, commit=True):

        if commit:
            user = self.cleaned_data['recipient']
            user.email_user(
                    getattr(settings, 'EMAIL_NOTIFICATION_SUBJECT_TEXT',
                        'HRP Notification'),
                    self.cleaned_data['text'],
                    from_email=getattr(settings, 'EMAIL_FROM_ADDRESS', self.user.email)
                )
