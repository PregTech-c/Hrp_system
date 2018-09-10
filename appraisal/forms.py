from django import forms
from django.forms.widgets import Textarea
from django.utils.translation import ugettext as _
from django.shortcuts import reverse

#from notify.signals import notify
import notify
from appraisal.models import *
from payroll.models import EmployeeProfile
from payroll.forms.hrp_widgets import *
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
            'description': forms.Textarea(attrs={'cols': 8, 'rows': 3})
        }

    service_line = ServiceLineChoiceField(
        queryset=ServiceLine.objects.all(),
        empty_label='-- All --',
        required=False
    )
    employee_profile = EmployeeModelChoiceField(
        queryset=EmployeeProfile.objects.all(),
        empty_label='-- All --',
        required=False
    )
    comment = forms.CharField(widget=Textarea(attrs={'rows': 4}))

    def clean(self):
        # Check that measures/qns were uploaded first
        if not AppraisalMeasure.objects.exists():
            raise forms.ValidationError(
                _('Measures/questions have not yet been setup.'),
                code='no_measures'
            )


    def save(self, commit=True):

        instance = super(AppraisalForm, self).save(commit=False)

        edit = False
        if instance.id:
            edit = True

        if commit:

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

                        notify.send(
                            'Appraisal',
                            recipient=profile.user,
#                            actor=self.reviewer,
                            actor_url=reverse('appraisal:received_employee_appraisal_measure_list',
                                kwargs={'emp_app_id': employee_appraisal.id}),
                            verb=' received from {}.'.format(self.reviewer.profile.get_fullname()),
                            actor_text='Appraisal',
                            nf_type='received_appraisal'
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

                notify.send(
                    'Appraisal',
                    recipient=instance.to_reviewer.user,
    #                            actor=self.reviewer,
                    actor_url=reverse('appraisal:received_employee_appraisal_measure_list',
                        kwargs={'emp_app_id': instance.employee_appraisal.id}),
                    verb=' review received from {}.'.format(instance.from_reviewer.get_fullname()),
                    actor_text='Appraisal',
                    nf_type='received_appraisal'
                )
        return instance

class CloseEmployeeAppraisalForm(forms.Form):
    remarks = forms.CharField(widget=Textarea)

class SearchAppraisalReportForm(forms.Form):
    appraisal = forms.ModelChoiceField(
        queryset=Appraisal.objects.all(),
        empty_label=None
    )
