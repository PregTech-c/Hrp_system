from django.views.generic import ListView, DetailView, View
from django.views.generic.list import MultipleObjectMixin
from django.views.generic.edit import (
    FormMixin,
    CreateView, 
    UpdateView, 
    DeleteView,
)
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.db.models import Q
from django.utils import timezone
from django.http import HttpResponse

from extra_views import CreateWithInlinesView, NamedFormsetsMixin

from digg_paginator import DiggPaginator

from recruitment.models import Vacancy, JobApplication, EvaluationStage
from recruitment.forms import (
    VacancyForm, 
    JobApplicationForm,
    EvaluationStageForm,
    JobApplicationUpdateForm, 
#    JobApplicationInlineFormSet, 
    JobApplicationSearchForm,
    JobApplicationDocumentInline
)

class VacancyListView(ListView):
    model = Vacancy
    paginator_class = DiggPaginator
    paginate_by = 10

class VacancyCreateView(SuccessMessageMixin, PermissionRequiredMixin,
        CreateView):
    model = Vacancy
    form_class = VacancyForm
    success_url = reverse_lazy('recruitment:vacancy_list', kwargs={'page': 1})
    success_message = "Vacancy has been created."
    permission_required = "payroll.hrp_manage_recruitment"

class VacancyUpdateView(SuccessMessageMixin, PermissionRequiredMixin,
        UpdateView):
    model = Vacancy
    form_class = VacancyForm
    success_url = reverse_lazy('recruitment:vacancy_list', kwargs={'page': 1})
    success_message = "Vacancy has been updated."
    permission_required = "payroll.hrp_manage_recruitment"

class VacancyDetailView(DetailView):
    model = Vacancy
        
class VacancyDeleteView(PermissionRequiredMixin, SuccessMessageMixin, 
        DeleteView):
    permission_required = 'recruitment.change_vacancy'
    model = Vacancy
    success_url = reverse_lazy('recruitment:vacancy_list', kwargs={'page': 1})
    success_message = '"The vacancy has been successfully deleted.'
    failure_message = '"The vacancy cannot be deleted because there ' \
        'are records that refer to it.'

"""Start Stages"""
class EvaluationStageView(SuccessMessageMixin, CreateView, MultipleObjectMixin):
    template_name = 'recruitment/evaluationstage_list.html'
    form_class = EvaluationStageForm
    pagination_class = DiggPaginator
    paginate_by = 10
    context_object_name = 'stages'
    success_message = "The evaluation stage has been added."
    
    def get_context_data(self, **kwargs):
        self.vacancy = Vacancy.objects.get(pk=self.kwargs.get('vac_id'))
        self.object_list = self.vacancy.evaluation_stages.all()
        context = super(EvaluationStageView, self).get_context_data(**kwargs)
        context.update({
            'vacancy': self.vacancy,
            'pg_url': "/recruitment/eval/{}/".format(self.vacancy.id),
        })
        return context

    def get_initial(self):
        initial = super(EvaluationStageView, self).get_initial()
        initial['vacancy'] = Vacancy.objects.get(pk=self.kwargs.get('vac_id'))
        initial['created_by'] = self.request.user.profile.id
        return initial
    
    def get_success_url(self):
        return reverse('recruitment:eval_list', 
            kwargs={'vac_id': self.kwargs.get('vac_id'), 'page': 1})

class EvaluationStageDeleteView(SuccessMessageMixin, PermissionRequiredMixin, 
        DeleteView):
    permission_required = 'recruitment.change_evaluationstage'
    model = EvaluationStage
    success_message = '"The stage has been successfully deleted.'
    failure_message = '"This stage cannot be deleted because there ' \
        'are records that refer to it.'

    def get_success_url(self):
        messages.success(self.request, self.success_message)
        return reverse('recruitment:eval_list', 
            kwargs={'vac_id': self.get_object().vacancy.id, 'page': 1})
        
### Start Job Applications
class JobApplicationListView(ListView):
    
    model = JobApplication
    paginator_class = DiggPaginator
    paginate_by = 5
    template_name = 'recruitment/jobapplication_list.html'

    def get_queryset(self):
        vacancy = get_object_or_404(Vacancy, pk=self.kwargs.get('vac_id'))
        self.vacancy = vacancy
        queryset = vacancy.applications.all()
        search_criteria = self.request.session.get('application_search')
        f = Q()

        if search_criteria:
            
            if self.kwargs.get('search') == 'off':
                del self.request.session['application_search']
            else:
                if search_criteria.get('stage'):
#                    s=ss
                    f = Q(evaluation_stage=search_criteria['stage'])
                if search_criteria.get('experience_years_threshold'):
                    f = Q(f&Q(experience_years__gt=int(
                        search_criteria['experience_years_threshold'])))
                if (search_criteria.get('gender') and 
                        search_criteria.get('gender') != 'A'):
                    f = Q(f&Q(gender=search_criteria['gender']))
                if search_criteria.get('age_lower_limit'):
                    f = Q(f&Q(date_of_birth__lte=timezone.now(
                        )-timezone.timedelta(
                            days=365.2425*search_criteria['age_lower_limit'])))
                if search_criteria.get('age_upper_limit'):
                    f = Q(f&Q(date_of_birth__gte=timezone.now(
                        )-timezone.timedelta(
                            days=365.2425*search_criteria['age_upper_limit'])))
        return queryset.filter(f)
    
    def get_context_data(self, **kwargs):
        context = super(JobApplicationListView, self).get_context_data(**kwargs)
        search_criteria = self.request.session.get('application_search')
        if search_criteria:
            form = JobApplicationSearchForm(search_criteria, vac_id=self.vacancy.id)
        else:
            form = JobApplicationSearchForm(vac_id=self.vacancy.id)
        if self.kwargs.get('show_form') == 'on':
            self.request.session['show_search_form'] = True
        elif self.kwargs.get('show_form') == 'off':
            try:
                del self.request.session['show_search_form']
            except:
                pass
            
        context.update({
            'show_search_form': 'on' if self.kwargs.get('show_form') == 'on' else 'off',
            'form': form,
            'vacancy': self.vacancy,
            'pg_url': "/recruitment/app/{}/".format(self.vacancy.id),
        })
        return context
    
    def post(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        vacancy = Vacancy.objects.get(pk=request.POST['vacancy_id'])
        form = JobApplicationSearchForm(request.POST, 
            vac_id=vacancy.id)
        if form.is_valid():
#            del request.session['application_search']
            request.session['application_search'] = form.cleaned_data
        else:
            ctx = self.get_context_data()
            ctx['form'] = form
            return render(request, self.template_name, ctx) 
        return super(JobApplicationListView, self).get(request, *args, **kwargs)
    
class ExternalJobApplicationCreateView(View):
    def post(self, request, *args, **kwargs):
        data = request.POST
        vacancy_id = data.get('vacancy')
        vacancy = Vacancy.objects.get(pk=vacancy_id)
        form = JobApplicationForm(request.POST, vacancy_id=vacancy_id)
        
#        vacancy.applications.create()
        if form.is_valid():
            form.save()
            return HttpResponse("Saved")
        else:
            return HttpResponse("Success")
    
class JobApplicationCreateView(NamedFormsetsMixin, PermissionRequiredMixin, 
        CreateWithInlinesView):
    model = JobApplication
    form_class = JobApplicationForm
    inlines = [JobApplicationDocumentInline, ]
    inlines_names = ['docs_formset',]
    success_url = reverse_lazy('recruitment:vacancy_list', kwargs={'page': 1})
    success_message = "The application has been submitted."
    permission_required = 'recruitment.change_jobapplication'

    def get_form_kwargs(self):
        kwargs = super(JobApplicationCreateView, self).get_form_kwargs()
        kwargs['vacancy_id'] = self.kwargs.get('vac_id')
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(JobApplicationCreateView, self).get_context_data(**kwargs)
        context.update({
            'vacancy': get_object_or_404(Vacancy, pk=self.kwargs.get('vac_id'))
        })
        return context

    def forms_valid(self, form, inlines):
        messages.success(self.request, self.success_message)
        return super(JobApplicationCreateView, self).forms_valid(form, inlines)

class JobApplicationExtCreateView(NamedFormsetsMixin, PermissionRequiredMixin, 
        CreateWithInlinesView):
    model = JobApplication
    form_class = JobApplicationForm
    inlines = [JobApplicationDocumentInline, ]
    inlines_names = ['docs_formset',]
    success_url = reverse_lazy('recruitment:vacancy_list', kwargs={'page': 1})
    success_message = "The application has been submitted."
    permission_required = 'recruitment.change_jobapplication'

    def get_form_kwargs(self):
        kwargs = super(JobApplicationCreateView, self).get_form_kwargs()
        kwargs['vacancy_id'] = self.kwargs.get('vac_id')
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(JobApplicationCreateView, self).get_context_data(**kwargs)
        context.update({
            'vacancy': get_object_or_404(Vacancy, pk=self.kwargs.get('vac_id'))
        })
        return context

    def forms_invalid(self, form, inlines):
        return HttpResponse("Failed {}".format(form.errors.__dict__))

    def forms_valid(self, form, inlines):
        return HttpResponse("Success")
        messages.success(self.request, self.success_message)
        return super(JobApplicationCreateView, self).forms_valid(form, inlines)

class JobApplicationDetailView(DetailView, FormMixin):
    model = JobApplication
    form_class = JobApplicationUpdateForm
    success_message = "The application has been moved to the {} stage."
    def get_context_data(self, **kwargs):
        context = super(JobApplicationDetailView, self).get_context_data(**kwargs)
        context['vacancy'] = self.object.vacancy
        return context
    
    def get_form_kwargs(self):
        return {
            'application_id': self.get_object().pk
        }
    
    def get_success_url(self):
        return reverse('recruitment:application_detail', 
            kwargs={'pk':self.get_object().pk})
    
    def post(self, request, *args, **kwargs):
        form = JobApplicationUpdateForm(request.POST, 
            application_id=self.get_object().pk)
        if form.is_valid():
            form.save()
            messages.success(self.request, self.success_message.format(form.cleaned_data['stage'].name))
        return super(JobApplicationDetailView, self).get(request, *args, **kwargs)
    