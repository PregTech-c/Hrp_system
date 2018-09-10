from django import forms

from extra_views import InlineFormSet

from recruitment.models import Vacancy, JobApplication, JobApplicationDocument
from recruitment.models import EvaluationStage, GENDER_CHOICES
from payroll.forms.hrp_widgets import JQueryUIDatepickerWidget

class VacancyForm(forms.ModelForm):
    
    class Meta:
        model = Vacancy
        exclude = ()
        widgets = {
            'fields_of_education': forms.Textarea(attrs={"rows":4}),
            'skills': forms.Textarea(attrs={"rows":4}),
            'job_description': forms.Textarea(attrs={"rows":4}),
            'due_date': JQueryUIDatepickerWidget,
        }
    def __init__(self, *args, **kwargs):
        super(VacancyForm, self).__init__(*args, **kwargs)
        self.fields['job_title'].empty_label = None
        self.fields['service_line'].empty_label = '-- None --'
        self.fields['reports_to'].empty_label = '-- None --'
#        self.fields['minimum_education'].empty_label = '-- None --'

class EvaluationStageForm(forms.ModelForm):
    class Meta:
        model = EvaluationStage
        exclude = ()
        widgets = {
            'vacancy': forms.HiddenInput,
            'created_by': forms.HiddenInput,
            'status': forms.HiddenInput
        }
        
class JobApplicationDocumentForm(forms.ModelForm):
    
    class Meta:
        model = JobApplicationDocument
        fields = ()
        widgets = {
            'job_application': forms.HiddenInput(),
        }

class JobApplicationForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        vacancy_id = kwargs.pop('vacancy_id')
        f = super(JobApplicationForm, self).__init__(*args, **kwargs)
        self.fields['vacancy'].initial = vacancy_id
        return f
    
    class Meta:
        model = JobApplication
        exclude = ()
        widgets = {
            'vacancy': forms.HiddenInput(),
            'education_fields': forms.Textarea(attrs={"rows":4}),
            'remarks': forms.Textarea(attrs={"rows":4}),
            'date_of_birth': JQueryUIDatepickerWidget
        }
        inlines = [JobApplicationDocumentForm,]

class JobApplicationDocumentInline(InlineFormSet):
    model = JobApplicationDocument
    fields = '__all__'
    widgets = {'remarks': forms.Textarea(attrs={"rows":4}),}

class JobApplicationUpdateForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        application_id = kwargs.pop('application_id')  
        super(JobApplicationUpdateForm, self).__init__(*args, **kwargs)
        self.job_application = JobApplication.objects.get(
            pk=application_id)
        self.fields['application_id'].initial = application_id
        self.fields['stage'].empty_label = None
        q = self.job_application.vacancy.evaluation_stages.filter(
            status='OPEN')
        if self.job_application.evaluation_stage is not None:
            q = q.filter(pk__gt=self.job_application.evaluation_stage.pk)
        self.fields['stage'].queryset = q
        
    application_id = forms.IntegerField(widget=forms.HiddenInput)
    stage = forms.ModelChoiceField(queryset=None)
    
    def save(self, commit=True):
#        instance = super(JobApplicationUpdateForm, self).save(commit=False)
        if commit:
            self.job_application.evaluation_stage = self.cleaned_data['stage']
            self.job_application.save()
        return self.job_application

class JobApplicationSearchForm(forms.Form):

    def __init__(self, *args, **kwargs):
        vac_id = kwargs.pop('vac_id') 
        super(JobApplicationSearchForm, self).__init__(*args, **kwargs)
        self.vacancy = Vacancy.objects.get(
            pk=vac_id)   
        self.fields['vacancy_id'].initial = vac_id
        self.fields['stage'].empty_label = '-- All --'
        self.fields['stage'].queryset = self.vacancy.evaluation_stages.all()
        
    stage = forms.ModelChoiceField(queryset=None, required=False)
    vacancy_id = forms.IntegerField(widget=forms.HiddenInput)
    experience_years_threshold = forms.IntegerField(required=False)
    age_lower_limit = forms.IntegerField(required=False)
    age_upper_limit = forms.IntegerField(required=False)
    gender = forms.ChoiceField(choices=(
                ('A', '-- Any --'),
                ('M', 'Male'),
                ('F', 'Female')
            ))