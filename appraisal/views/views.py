from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import FormMixin,FormView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.urlresolvers import reverse_lazy, reverse
from django.shortcuts import redirect
from django.utils import timezone
from django.http import HttpResponse
from django.shortcuts import render
from easy_pdf.views import PDFTemplateView

from reportlab.pdfgen import canvas
from digg_paginator import DiggPaginator

from appraisal.models import *
from appraisal.forms import *

PGN = {'body': 10, 'padding': 1, 'tail': 5, 'padding': 2}

class AppraisalListView(PermissionRequiredMixin, ListView):
    permission_required = 'payroll.hrp_manage_appraisals'
    model = Appraisal
    context_object_name = 'appraisal_list'
    paginate_by = 5
    template_name = 'appraisal_list.html'

    def get_context_data(self, **kwargs):
        context = super(AppraisalListView, self).get_context_data(**kwargs)
        context['paginator'] = DiggPaginator(self.get_queryset(),
            self.paginate_by,
            body=PGN['body'], tail=PGN['tail'], padding=PGN['padding']
            ).page(self.kwargs.get('page', 1))
        return context

class AppraisalCreateView(PermissionRequiredMixin, SuccessMessageMixin,
        CreateView):
    permission_required = 'payroll.hrp_manage_appraisals'
    form_class = AppraisalForm
    success_url = reverse_lazy('appraisal:appraisal_list')
    template_name = 'appraisal_form.html'
    success_message = 'Appraisal has been successfully initiated.'

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(AppraisalCreateView, self).get_form_kwargs(*args, **kwargs)
        kwargs['reviewer'] = self.request.user
        return kwargs

class AppraisalUpdateView(SuccessMessageMixin, UpdateView):
    model = Appraisal
    form_class = AppraisalForm
    success_url = reverse_lazy('appraisal:appraisal_list')
    template_name = 'appraisal_form.html'
    success_message = 'Appraisal has been successfully modified.'

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(AppraisalUpdateView, self).get_form_kwargs(*args, **kwargs)
        kwargs['reviewer'] = self.request.user
        return kwargs

class AppraisalDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'payroll.hrp_manage_appraisals'
    model = Appraisal
    template_name = 'appraisal_confirm_delete.html'
    success_url = reverse_lazy('appraisal:appraisal_list')
    success_message = '"%(description)s" has been successfully deleted.'
    failure_message = '"%(description)s" cannot be deleted because there ' \
        'are records that refer to it.'

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        try:
            view = super(AppraisalDeleteView, self).delete(request,
                *args, **kwargs)
        except IntegrityError as e:
            messages.error(request, self.failure_message % obj.__dict__)
            return reverse('appraisal:appraisal_list')
        else:
            messages.success(request, self.success_message % obj.__dict__)
            return view
# ===

class EmployeeAppraisalListView(ListView):
    context_object_name = 'employee_appraisal_list'
    paginate_by = 5
    template_name = 'employee_appraisal_list.html'

    def get_queryset(self):
        profile = getattr(self.request.user, 'profile', None)
        if profile:
#            appraisals = profile.get_appraisals(status='ongoing')
            appraisals = profile.get_appraisals(status='all')
            return appraisals
            arr = []
            for appraisal in appraisals:
                try:
                    if appraisal.flows.order_by('-id')[0].to_reviewer == self.request.user.profile:
                        arr.append(appraisal.id)
                except:
                    pass

            return EmployeeAppraisal.objects.filter(pk__in=arr).order_by('-id')
        return EmployeeAppraisal.objects.none()

    def get_context_data(self, **kwargs):
        context = super(EmployeeAppraisalListView,
            self).get_context_data(**kwargs)
        context['paginator'] = DiggPaginator(self.get_queryset(),
            self.paginate_by,
            body=PGN['body'], tail=PGN['tail'], padding=PGN['padding']
            ).page(self.kwargs.get('page', 1))
        return context

class EmployeeAppraisalMeasureView(ListView):
    context_object_name = 'employee_appraisal_measure_list'
    paginate_by = 5
    template_name = 'employee_appraisal_measure_list.html'
    appraisal = None

#    def get_template_names(self):
#        if self.emp_appraisal.is_complete:
#            return 'received_appraisal_measure_list.html'
#        return 'employee_appraisal_measure_list.html'

    def get_queryset(self):
        emp_app_id = self.kwargs.get('emp_app_id')
        emp_app = EmployeeAppraisal.objects.get(pk=emp_app_id)
        self.emp_appraisal = emp_app
        return emp_app.measures.filter(
            reviewer=self.request.user.profile).order_by('-id')

    def get_context_data(self, **kwargs):
        context = super(EmployeeAppraisalMeasureView,
            self).get_context_data(**kwargs)

        reviewed = self.emp_appraisal.get_total_answered(
            reviewer=self.request.user.profile)
        total = self.emp_appraisal.measures.filter(
            reviewer=self.request.user.profile).count()

        remarks = {
            'open': {
                'initiator': self.emp_appraisal.flows.order_by('id')[0].from_reviewer,
                'date': self.emp_appraisal.flows.order_by('id')[0].created_at,
                'comment': self.emp_appraisal.on_open_remarks,
            },
            'close': {
                'closed_by': self.emp_appraisal.flows.order_by('-id')[0].to_reviewer,
                'date': self.emp_appraisal.closed_on,
                'comment': self.emp_appraisal.on_close_remarks
            },
        }
        is_closed = False
        if self.emp_appraisal.is_complete is True:
            is_closed = True

        show_submit = False
        if not is_closed and (self.request.user.profile.reports_to and
            reviewed == total) and self.emp_appraisal.get_has_appraisal() == self.request.user.profile and total:
            show_submit = True

        extra_context = {
            'is_closed': is_closed,
            'remarks': remarks,
            'emp_appraisal': self.emp_appraisal,
            'total_measures_reviewed': reviewed,
            'total_measures': total,
            'paginator': DiggPaginator(self.get_queryset(),
            self.paginate_by,
            body=PGN['body'], tail=PGN['tail'], padding=PGN['padding']
            ).page(self.kwargs.get('page', 1))
        }
        context.update(extra_context)
        if show_submit:
            profile = self.request.user.profile
            context.update({
                'show_submit': show_submit,
                'form': EmployeeAppraisalFlowForm(initial={
                    'from_reviewer': profile,
                    'to_reviewer': profile.reports_to,
                    'employee_appraisal': self.emp_appraisal
                })
            })

        return context

class EmployeeAppraisalMeasurePdfView(PDFTemplateView):
    template_name = "employee_appraisal_measure_pdf_list.html"
    context_object_name = 'employee_appraisal_measure_list'

    def get_context_data(self, **kwargs):
        emp_app_id = self.kwargs.get('emp_app_id')
        emp_app = EmployeeAppraisal.objects.get(pk=emp_app_id)
        self.emp_appraisal = emp_app
        m_list = emp_app.measures.filter(
            reviewer=self.request.user.profile).order_by('-id')
        context = super(EmployeeAppraisalMeasurePdfView, self).get_context_data(
            pagesize='A4',
#            title='Hi there!',
            **kwargs
        )
        remarks = {
            'open': {
                'initiator': self.emp_appraisal.flows.order_by('id')[0].from_reviewer,
                'date': self.emp_appraisal.flows.order_by('id')[0].created_at,
                'comment': self.emp_appraisal.on_open_remarks,
            },
            'close': {
                'closed_by': self.emp_appraisal.flows.order_by('-id')[0].to_reviewer,
                'date': self.emp_appraisal.closed_on,
                'comment': self.emp_appraisal.on_close_remarks
            },
        }
        context.update({
            'is_closed': self.emp_appraisal.is_complete,
            'emp_appraisal': emp_app,
            'employee_appraisal_measure_list': m_list,
            'self_score': self.emp_appraisal.get_average_rating(
                reviewer=self.emp_appraisal.employee_profile),
            'supervisor_score': self.emp_appraisal.get_average_rating(
                reviewer=self.emp_appraisal.employee_profile.reports_to),
            'remarks': remarks,
            'comments': self.emp_appraisal.flows.filter(comment__isnull=False).order_by('-id'),
        })
        return context
#    def get_queryset(self):
#        emp_app_id = self.kwargs.get('emp_app_id')
#        emp_app = EmployeeAppraisal.objects.get(pk=emp_app_id)
#        self.emp_appraisal = emp_app
#        return emp_app.measures.filter(
#            reviewer=self.request.user.profile).order_by('-id')

class EmployeeAppraisalMeasureUpdateView(SuccessMessageMixin, UpdateView):
    model = EmployeeAppraisalMeasure
    form_class = EmployeeAppraisalMeasureForm
    template_name = 'employee_appraisal_measure_form.html'
    success_url = reverse_lazy('appraisal:employee_appraisal_measure_list')
    success_message = 'The appraisal parameter has been updated.'
    context_object_name = 'emp_appraisal_measure'

    def form_valid(self, form):
        form.instance.reviewer = self.request.user.profile
        return super(EmployeeAppraisalMeasureUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('appraisal:employee_appraisal_measure_list',
            kwargs={'emp_app_id': self.get_object().employee_appraisal.id})

    def get_context_data(self):
        context = super(EmployeeAppraisalMeasureUpdateView,
            self).get_context_data()
        context['emp_appraisal'] = self.get_object()
        return context

## Supervisor views
class ReceivedEmployeeAppraisalMeasureView(SuccessMessageMixin, ListView,
        FormView):
    context_object_name = 'appraisal_measure_list'
    paginate_by = 5
    template_name = 'received_appraisal_measure_list.html'
    appraisal = None

    form_class = CloseEmployeeAppraisalForm
    success_message = 'The appraisal has been closed.'
#    success_url = reverse_lazy('appraisal:employee_appraisal_list')

    def get_queryset(self):
        emp_app_id = self.kwargs.get('emp_app_id')
        emp_app = EmployeeAppraisal.objects.get(pk=emp_app_id)
        self.emp_appraisal = emp_app
        if self.request.user.profile == emp_app.employee_profile:
            reviewer = self.request.user.profile.reports_to
        else:
            reviewer = self.request.user.profile
        return emp_app.measures.filter(reviewer=reviewer.id)

    def get_context_data(self, **kwargs):
        context = super(ReceivedEmployeeAppraisalMeasureView,
            self).get_context_data(**kwargs)

        reviewed = self.emp_appraisal.get_total_answered(
            reviewer=self.request.user.profile)
        total = self.emp_appraisal.measures.filter(
            reviewer=self.request.user.profile).count()

#        comments =  self.emp_appraisal.flows.all()
        is_closed = False
        if self.emp_appraisal.is_complete is True:
            is_closed = True

        remarks = {
            'open': {
                'initiator': self.emp_appraisal.flows.order_by('id')[0].from_reviewer,
                'date': self.emp_appraisal.flows.order_by('id')[0].created_at,
                'comment': self.emp_appraisal.on_open_remarks
            },
            'close': {
                'closed_by': self.emp_appraisal.flows.order_by('-id')[0].to_reviewer,
                'date': self.emp_appraisal.closed_on,
                'comment': self.emp_appraisal.on_close_remarks
            },
        }

        extra_context = {
            'remarks': remarks,
            'is_closed': is_closed,
            'emp_appraisal': self.emp_appraisal,
            'total_measures_reviewed': reviewed,
            'comments': self.emp_appraisal.flows.filter(comment__isnull=False).order_by('-id'),
            'total_measures': total,
            'self_score': self.emp_appraisal.get_average_rating(
                reviewer=self.emp_appraisal.employee_profile),
            'adjusted_score': self.emp_appraisal.get_average_rating(),
            'paginator': DiggPaginator(self.get_queryset(),
            self.paginate_by,
            body=PGN['body'], tail=PGN['tail'], padding=PGN['padding']
            ).page(self.kwargs.get('page', 1))
        }
        context.update(extra_context)

        return context

    def form_valid(self, form):
        emp_app_id = self.kwargs.get('emp_app_id')
        emp_appraisal = EmployeeAppraisal.objects.get(pk=emp_app_id)

        emp_appraisal.on_close_remarks = form.cleaned_data['remarks']
        emp_appraisal.closed_on = timezone.now()
        emp_appraisal.status = '0' # complete
        emp_appraisal.save()
        return redirect('appraisal:received_employee_appraisal_list')

class ReceivedAppraisalMeasureUpdateView(SuccessMessageMixin, UpdateView):
    model = EmployeeAppraisalMeasure
    form_class = EmployeeAppraisalMeasureForm
    template_name = 'received_appraisal_measure_form.html'
    success_message = 'The appraisal parameter has been updated.'
    context_object_name = 'emp_appraisal_measure'

    def form_valid(self, form):
#        form.instance.reviewer = self.request.user.profile
        return super(ReceivedAppraisalMeasureUpdateView,
            self).form_valid(form)

    def get_initial(self):
        return {'reviewer': self.request.user.profile}
#    def get_form_kwargs(self):
#        return {'reviewer': self.request.user.profile}

    def get_success_url(self):
        return reverse('appraisal:received_employee_appraisal_measure_list',
            kwargs={'emp_app_id': self.get_object(
                ).employee_appraisal.id})

# Flow management
class AppraisalFlowCreateView(SuccessMessageMixin, CreateView):
#    permission_required = 'payroll.hrp_manage_appraisals'
    model = EmployeeAppraisalFlow
    form_class = EmployeeAppraisalFlowForm
    success_url = reverse_lazy('appraisal:employee_appraisal_list')
    success_message = 'Appraisal has been successfully submitted.'
    template_name = 'employee_appraisal_list.html' # Useless

#    def form_invalid(self, form):
#
#        s=ss
#        return
#    def get_initial(self):
#        initial = super(AppraisalFlowCreateView, self).get_initial()
##        s=ss
#        profile = self.request.user.profile
#        initial.update({
#            'from_reviewer': 5,
#            'to_reviewer': profile.reports_to
#        })
#        return initial
#    def get_success_url(self):
#        return reverse('appraisal:employee_appraisal_measure_list',
#            kwargs={'emp_app_id': self.get_object(
#                ).employee_appraisal.id})

class ReceivedEmployeeAppraisalListView(ListView):
    context_object_name = 'employee_appraisal_list'
    paginate_by = 5
    template_name = 'received_employee_appraisal_list.html'

    def get_queryset(self):
        profile = getattr(self.request.user, 'profile', None)
        if profile:
            return profile.get_received_appraisals()
        return EmployeeAppraisal.objects.none()

    def get_context_data(self, **kwargs):
        context = super(ReceivedEmployeeAppraisalListView,
            self).get_context_data(**kwargs)
        context['paginator'] = DiggPaginator(self.get_queryset(),
            self.paginate_by,
            body=PGN['body'], tail=PGN['tail'], padding=PGN['padding']
            ).page(self.kwargs.get('page', 1))
        return context

class PerformanceClassificationView(SuccessMessageMixin, CreateView):
    model = PerformanceClassification
    form_class = PerformanceClassificationForm
    success_url = reverse_lazy('appraisal:employee_appraisal_list')
#    success_message = 'Appraisal has been successfully submitted.'
    template_name = 'performance_classification.html' # Useless
