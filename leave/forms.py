__author__ = "Steven Kawuma <kawuma@gmail.com>"
__date__ = "Feb 14, 2017 3:16:22 PM"

from django.contrib.auth.models import User, Permission
from django.db.models import Q
from django.forms import *
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from leave.models import *
from payroll.forms.hrp_widgets import *
from payroll.forms.hrp_fields import EmployeeChoiceField

class HolidayForm(ModelForm):

    class Meta:
        model = Holiday
        exclude = ()
        widgets = {
            'date': JQueryUIDatepickerWidget,
        }

class LeavePeriodForm(ModelForm):

    class Meta:
        model = LeavePeriod
        exclude = ()
        widgets = {
            'start_date': JQueryUIDatepickerWidget,
            'end_date': JQueryUIDatepickerWidget,
        }

    def clean(self):
        data = self.cleaned_data
        leave_periods = LeavePeriod.objects.order_by('-id')
        if leave_periods.exists():
            last_leave_period = leave_periods[0]
            if data['start_date'] <= last_leave_period.end_date:
                raise(ValidationError('Leave periods do may not overlap.'))
        
        if data['start_date'] >= data['end_date']:
            raise(ValidationError('Start date may not be greater than the end '
                'date.'))
                
        return data
            
                
class LeaveTypeForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(LeaveTypeForm, self).__init__(*args, **kwargs)
        self.fields['gender'].empty_label = '-- All --'
        
    class Meta:
        model = LeaveType
        exclude = ()

class EmployeeProfileModelChoiceField(ModelChoiceField):
    model = LeaveApprover
    
    def label_from_instance(self, obj):
            return "{}, {}, {}".format(obj.get_fullname(), obj.position,
                obj.service_line)
        

class LeaveApproverForm(ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(LeaveApproverForm, self).__init__(*args, **kwargs)
        self.fields['profile'].queryset = EmployeeProfile.objects.exclude(
            pk__in=[
                approver.profile.pk for approver in LeaveApprover.objects.all()
                ])
            
    class Meta:
        model = LeaveApprover
        exclude = ()
    
    profile = EmployeeProfileModelChoiceField(
        queryset=EmployeeProfile.objects.all(), empty_label = None)

class LeaveRequestForm(ModelForm):
    
    def __init__(self, *args, **kwargs):
        
        leave_type_queryset = kwargs.pop('leave_type_queryset')
        
        super(LeaveRequestForm, self).__init__(*args, **kwargs)
        self.fields['profile'].widget = HiddenInput()
        self.fields['leave_period'].empty_label = None
        self.fields['leave_type'].empty_label = None
        self.fields['leave_type'].queryset = leave_type_queryset
        self.fields['start_date'].required = True
        self.fields['end_date'].required = True
        self.fields['comment'].required = False
            
    class Meta:
        model = LeaveRequest
        exclude = ()
        widgets = {
            'start_date': JQueryUIDatepickerWidget,
            'end_date': JQueryUIDatepickerWidget,
        }
    
#    def clean_start_date(self):
#        ss
#        data = self.cleaned_data['start_date']
#        if 1: #data is None:
#            raise ValidationError('Start date is required.')
#        return data
    
    def clean(self):
        cleaned_data = super(LeaveRequestForm, self).clean()
        leave_period = cleaned_data.get('leave_period')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        profile = cleaned_data.get('profile')
        leave_type = cleaned_data.get('leave_type')
        

        perm = Permission.objects.get(codename='hrp_handle_leave_requests')
        approvers = User.objects.filter(
            Q(Q(groups__permissions=perm)|
            Q(user_permissions=perm)),
            profile__isnull=False
        )
        if not approvers:
            raise(ValidationError('There are no leave approvers registered.'
                ' Contact your System Administrator'))
                
        if start_date <= leave_period.start_date:
            raise(ValidationError(
                'The start date is beyond the specified leave period.'))

        if end_date >= leave_period.end_date:
            raise(ValidationError(
                'The end date is beyond the specified Leave Period.'))

        if start_date >= end_date:
            raise(ValidationError(
                'The end date may not be nearer than the start date.'))

        d = start_date
        no_of_days_requested = 0 
        weekend = set([5, 6])
        hols = Holiday.objects.all()
        while(d < end_date):
            d += timezone.timedelta(1)
#            if d.weekday() not in weekend:
#                no_of_days_requested += 1
            
            for request in profile.leave_requests.all_accepted():
                if d >= request.start_date and d <= request.end_date:
                    raise(ValidationError("Requested period overlaps with "
                        "{}, {} {}.".format(
                            request.leave_type,
                            request.start_date,
                            request.end_date
                            )
                    ))

            if d.weekday() in weekend or d in \
                [day.date for day in hols.filter(recurring=False)]:
                continue
            if d.strftime('%m%d') in \
                [day.date.strftime('%m%d') for day in hols.filter(recurring=True)]:
                continue
            no_of_days_requested += 1
                        
        if leave_type.count_no_of_days_left(profile=profile) <\
            no_of_days_requested:
            raise(ValidationError("You requested for {} days which exceed "
                "the {} days allowed for this leave type.".format(
                no_of_days_requested, int(leave_type.no_of_days)))
            )
        
        return cleaned_data

class LeaveApplicationReviewForm(ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(LeaveApplicationReviewForm, self).__init__(*args, **kwargs)
        choices = set(self.fields['leave_status'].choices)
        choices.remove(('P', 'Pending'))
        choices.remove(('E', 'Expired'))
        choices.remove(('C', 'Canceled'))
        self.fields['leave_status'].choices = choices 
        
    class Meta:
        model = LeaveApplicationReview
        widgets = {
            'request': HiddenInput(),
            'reviewer': HiddenInput(),
            'reviewed_at': HiddenInput()
        }
        exclude = ()

class OnLeaveReportForm(Form):
    
    start_date = CharField(required=False, widget=JQueryUIDatepickerWidget())    
    end_date = CharField(required=False, widget=JQueryUIDatepickerWidget())
    employee = EmployeeChoiceField()
    
    def clean(self):
        data = self.cleaned_data
        
        if bool(data.get('start_date')) ^ bool(data.get('end_date')):
            raise ValidationError(
                _("Enter both dates, or none to ignore the time period.")
            )
            
        if data.get('start_date') > data.get('end_date'):
            raise ValidationError(
                _("Start date my not be greater than the end date.")
            )

class EmployeeChoiceField1(ModelChoiceField):
    
    def __init__(self, obj_label=None, *args, **kwargs):
        super(EmployeeChoiceField1, self).__init__(self, *args, **kwargs)
        self.queryset = EmployeeProfile.objects.order_by('user__last_name')
        self.obj_label = obj_label
        self.empty_label = None
        self.required = False
    
    def label_from_instance(self, obj):
        return "{} ({})".format(obj.get_fullname(), obj.position)

class EmployeeLeaveDaysForm(Form):

    employee = EmployeeChoiceField1(empty_label=None)
    leave_period = ModelChoiceField(queryset=LeavePeriod.objects.all(), 
        empty_label=None)
    
