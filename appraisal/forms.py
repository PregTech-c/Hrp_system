from django import forms
from django.forms.widgets import Textarea
from django.forms import ModelForm, ValidationError
from django.utils.translation import ugettext_lazy as _

from appraisal.models import *
from payroll.models import EmployeeProfile
from payroll.forms.hrp_widgets import *
from payroll.forms.employee_forms import HrpModelMultipleChoiceField
from payroll.forms.hrp_fields import ServiceLineChoiceField, EmployeeModelChoiceField

class AppraisalForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        reviewer = kwargs.pop('reviewer')
        super(AppraisalForm, self).__init__(*args, **kwargs)
        self.reviewer = reviewer

    class Meta:
        model = Appraisal
        exclude = ()
        widgets = {
            'start_date': JQueryUIDatepickerWidget,
            'end_date': JQueryUIDatepickerWidget,
            'due_date': JQueryUIDatepickerWidget,
        }

#    service_line = HrpModelMultipleChoiceField(
#        queryset=ServiceLine.objects.all(),
    #    empty_label='-- All --',
#        required=False
#    )
    employee_profile = EmployeeModelChoiceField(
        queryset=EmployeeProfile.objects.all(),
        empty_label='-- All --',
        required=False
    )
    comment = forms.CharField(widget=Textarea(attrs={'rows': 4}))

    def save(self, commit=True):

        instance = super(AppraisalForm, self).save(commit=False)

        edit = False
        if instance.id:
            edit = True

        if commit:

            # Check that measures/qns were uploaded first
    #        if not AppraisalMeasure.objects.exists():
    #            raise ValidationError(
    #                _('Measures/questions have not yet been setup.'),
    #                code='no_measures'
    #            )
            instance.save()

            if edit is False:

                if instance.service_line:
                    profiles = instance.service_line.employee_profiles.all()
                elif instance.employee_profile:
                    profiles = profiles.filter(id__in=[instance.employee_profile.id])
                else:
                    profiles = EmployeeProfile.objects.all()

                for profile in profiles:
                    if profile.reports_to:
                        employee_appraisal = profile.appraisals.create(
                            appraisal=instance,
                            on_open_remarks = self.cleaned_data['comment']
                        )

                        flow = employee_appraisal.flows.create(
                            from_reviewer=self.reviewer.profile,
                            to_reviewer=profile
                        )

                        for measure in profile.position.measure_definitions.all():
                            employee_appraisal.measures.create(
                                measure=measure,
                                reviewer=profile
                            )

        return instance

class AppraisalParameterForm(forms.ModelForm):
    class Meta:
        model = AppraisalParameter
        exclude = ()

class AppraisalMeasureForm(forms.ModelForm):
    class Meta:
        model = AppraisalMeasure
        exclude = ()

    service_line = ServiceLineChoiceField(
        queryset=ServiceLine.objects.all(),
        empty_label='-- All --',
        required=False,

    )

    def __init__(self, *args, **kwargs):
        super(AppraisalMeasureForm, self).__init__(*args, **kwargs)
        self.fields['parameter'].empty_label = None
        self.fields['position'].empty_label = None

class EmployeeAppraisalMeasureForm(forms.ModelForm):

    class Meta:
        model = EmployeeAppraisalMeasure
        exclude = ()
        widgets = {
            'employee_appraisal': forms.HiddenInput,
            'measure': forms.HiddenInput,
            'reviewer': forms.HiddenInput,
        }

    def save(self, commit=True):
        instance = super(EmployeeAppraisalMeasureForm, self).save(commit=False)
        if commit:
            instance.save()
            emp_appraisal = instance.employee_appraisal
            if emp_appraisal.status == '1':
                emp_appraisal.status = '3'
                emp_appraisal.save()
        return instance

#class SupervisorAppraisalMeasureForm(forms.ModelForm):
#
##    def __init__(self, *args, **kwargs):
##        reviewer = kwargs.pop('reviewer')
##        super(SupervisorAppraisalMeasureForm, self).__init__(*args, **kwargs)
##        self.fields['reviewer'].value = reviewer
#
#    class Meta:
#        model = SupervisorAppraisalMeasure
#        exclude = ()
#        widgets = {
#            'employee_appraisal_measure': forms.HiddenInput,
#            'measure': forms.HiddenInput,
#            'reviewer': forms.HiddenInput,
#        }
##
##    def save(self, commit=True):
##        instance = super(SupervisorAppraisalMeasureForm, self).save(commit=False)
##        if commit:
##            instance.save()
##            emp_appraisal = instance.measure.employee_appraisal
##            emp_appraisal.status = '0'
##            emp_appraisal.save()
##        return instance

class EmployeeAppraisalFlowForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        status = None
        if kwargs.get('status'):
            status = kwargs.pop('status')

        super(EmployeeAppraisalFlowForm, self).__init__(*args, **kwargs)
        self.status = status

    class Meta:
        model = EmployeeAppraisalFlow
        exclude = ('created_at',)
        widgets = {
            'employee_appraisal': forms.HiddenInput,
            'from_reviewer': forms.HiddenInput,
            'to_reviewer': forms.HiddenInput,
        }

    def save(self, commit=True):
        instance = super(EmployeeAppraisalFlowForm, self).save(commit=False)
        if commit:
            instance.save()
            if instance.to_reviewer:
                for measure in instance.employee_appraisal.measures.all():
                    instance.employee_appraisal.measures.create(
                        measure=measure.measure,
                        reviewer=instance.to_reviewer
                    )
        return instance

class CloseEmployeeAppraisalForm(forms.Form):
    remarks = forms.CharField(widget=Textarea)

class PerformanceClassificationForm(forms.ModelForm):

    class Meta:
        model = PerformanceClassification
        exclude = ()
