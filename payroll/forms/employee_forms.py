import random
import string

from payroll.models import Position, EmployeeTitle, Nationality
from payroll.models import EmployeeProfile, NextOfKin, EmployeeDocument

from django.contrib.auth.models import User, Permission
from django.forms import *
from django.utils import timezone
from django.forms import modelformset_factory
from django.conf import settings

from .hrp_widgets import *

class EmployeeSearchListForm(Form):
    emp_name = CharField(min_length=10)

class PositionForm(ModelForm):
    class Meta:
        model = Position
        exclude = ()
        widgets = {
            'name': TextInput(attrs={'size': '60'}),
        }
        
class NextOfKinForm(ModelForm):
    class Meta:
        model = NextOfKin
        exclude = ()
        
    def __init__(self, *args, **kwargs):
        super(NextOfKinForm, self).__init__(*args, **kwargs)
        self.error_class = DivErrorList

class NationalityForm(ModelForm):
    
    class Meta:
        model = Nationality
        exclude = ()
        widgets = {
            'name': TextInput(attrs={'size': '60'}),
        }       
            
class EmployeeTitleForm(ModelForm):
    class Meta:
        model = EmployeeTitle
        exclude = ()
        widgets = {
            'name': TextInput(attrs={'size': '60'}),
        }

class HrpModelMultipleChoiceField(ModelMultipleChoiceField):

    def label_from_instance(self, obj):
        return u'{}'.format(obj.name) # e.g. 'Can change article'
    
class EmployeeForm(ModelForm):

    create_login = BooleanField(required=False,
        widget=CheckboxInput(attrs={'onClick': 'return toggle();'}))

    def __init__(self, *args, **kwargs):
        super(EmployeeForm, self).__init__(*args, **kwargs)
        self.error_class = DivErrorList
        self.fields['last_name'].required = True
        self.fields['first_name'].required = True
#        self.fields['username'].required = False
        self.fields['password'].required = False
        self.fields['email'].required = True
        self.fields['is_staff'].initial = False

#        self.fields['user_permissions'] = HrpModelMultipleChoiceField(
#            queryset=Permission.objects.filter(codename__startswith='hrp'),
#            widget=PCheckboxSelectMultiple(),
#            required=False
#        )
        
    class Meta:
        model = User
        exclude = ('is_active',
                    'is_superuser', 'last_login', 'date_joined')

        widgets = {
            'first_name': TextInput(attrs={'size': 60}),
            'last_name': TextInput(attrs={'size': 60}),
            'username': TextInput(attrs={'size': 60}),
#            'is_staff': CheckboxInput(attrs={'onClick': 'return toggle();'}),
            'email': TextInput(attrs={'size': 60}),
            'password': HiddenInput,
#            'user_permissions': PCheckboxSelectMultiple,
        }

#    def is_valid(self):
#        cleaned_data = self.cleaned_data
#        if cleaned_data['is_staff']:
#            cleaned_data['password'] = ''.join(random.choice(
#                    string.letters+string.digits) for i in xrange(6))
#        return super(EmployeeForm, self).is_valid()


#    def clean(self):
#        if not self.cleaned_data['is_staff']:
#
#            self.cleaned_data['username'] = ''.join(random.choice(
#                    string.letters+string.digits) for i in xrange(6))
#        else:
#            if not self.cleaned_data['username']:
#                self._errors['username'] = ErrorList(['Username is required'])
#                del self.cleaned_data['username']
#            else:
#                self.set_password'] = User.objects.make_random_password(10)


#        return self.cleaned_data

    def save(self, force_insert=False, commit=True):

        user = super(EmployeeForm, self).save(commit=False)
        if commit:
            if not self.instance.pk and 0:
                password = User.objects.make_random_password(6)
                user.set_password(password)

                email_msg = u"""Hello {},

Below are your authentication details to the HR and Payroll Management portal:

Username: {}
Password: {}

Please note that both username and password are case sensitive.

You may change the password after login.

Management""".format(
                    self.cleaned_data['first_name'],
                    self.cleaned_data['username'], 
                    password
                )

                email_error_msg = ''
                try:
                    user.email_user(getattr(settings, 
                        'EMAIL_NOTIFICATION_SUBJECT_TEXT', 'HRP Notification'), 
                        email_msg, from_email=settings.EMAIL_FROM_ADDRESS)
                except Exception as e:
                    email_error_msg = ' Failed to send password email.'
            user.save()
            
            if self.cleaned_data['user_permissions']:

                user.user_permissions.clear()
                for perm_id in self.cleaned_data['user_permissions']:
                    user.user_permissions.add(perm_id)

        return user

class ReportsToModelChoiceField(ModelChoiceField):
    model = EmployeeProfile()
    def label_from_instance(self, obj):
        return "{}, {}".format(obj.get_fullname(), obj.position)
    
class EmployeeProfileForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(EmployeeProfileForm, self).__init__(*args, **kwargs)
        self.error_class = DivErrorList
        self.fields['marital_status'].empty_label = None
        self.fields['nationality'].empty_label = None
        self.fields['education_level'].empty_label = 'None'
        
    reports_to = ReportsToModelChoiceField(
        queryset=EmployeeProfile.objects.order_by('user__last_name'), 
        empty_label='None',
        required=False
    )
    user = IntegerField(widget=HiddenInput, required=False)

    class Meta:
        model = EmployeeProfile
        exclude = ('employee_type', 'allowances', 'deductions')

        widgets = {
            'bank_account_number': TextInput(attrs={'size': '60'}),
            'nssf_number': TextInput(attrs={'size': '60'}),
            'tin_number': TextInput(attrs={'size': '60'}),
            'phone_number': TextInput(attrs={'size': 60}),
            'employee_number': TextInput(attrs={'size': 60}),
            'other_names': TextInput(attrs={'size': 60}),
            'employed_on': JQueryUIDatepickerWidget,
            'date_of_birth': JQueryUIDatepickerWidget,
#            'documents': ClearableFileInput(attrs={'multiple': True}),
#            'deductions': admin.widgets.FilteredSelectMultiple('deductions', False),
#            'deductions': PCheckboxSelectMultiple

        }

    def clean_employed_on(self):
        data = self.cleaned_data['employed_on']

        if data:
            if data > timezone.now():
                raise ValidationError(
                    'Employment date may not be in the future.')

        return data

    def clean_bank_account_number(self):
        data = self.cleaned_data['bank_account_number']
        if len(data) < 5:
            raise ValidationError('Bank Account Number should be at'
                    ' least 5 characters')
        return data

    def clean_nssf_number(self):
        data = self.cleaned_data['nssf_number']
        if len(data) < 5:
            raise ValidationError('NSSF Number should be at'
                    ' least 5 characters')
        return data

    def clean_tin_number(self):
        data = self.cleaned_data['tin_number']
        if len(data) < 5:
            raise ValidationError('TIN Number should be at'
                    ' least 5 characters')
        return data

#    def save(self, commit=True):
#        profile = super(EmployeeProfileForm, self).save(commit=False)
#        if commit:
#            profile.save()
#            
#            for role in profile.roles:
#                profile.add(role)
#        return profile

class EmployeePhotoForm(Form):
    
    photo = FileField()
    employee_profile_id = IntegerField(widget=HiddenInput)
    
    def save(self, commit=True):

        if commit:
            profile = EmployeeProfile.objects.get(pk=self.cleaned_data['employee_profile_id'])
            profile.photo = self.cleaned_data['photo']
            profile.save()
#            s=ss
        return profile
    
class EmployeeDocumentForm(ModelForm):
    class Meta:
        model =  EmployeeDocument
        exclude = ('description',)
        widgets = {
            'employee_profile': HiddenInput()
        }

EmployeeDocumentFormSet = modelformset_factory(EmployeeDocument,
    exclude=('employee_profile',), extra=4)

