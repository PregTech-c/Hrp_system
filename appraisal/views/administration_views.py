from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse_lazy

from digg_paginator import DiggPaginator

from appraisal.models import *
from appraisal.forms import *

PGN = {'body': 10, 'padding': 1, 'tail': 5, 'padding': 2}

class AppraisalParameterListView(ListView):
    model = AppraisalParameter
    context_object_name = 'appraisal_parameter_list'
    paginate_by = 5
    template_name = 'administration/appraisal_parameter_list.html'

    def get_context_data(self, **kwargs):
        context = super(AppraisalParameterListView, 
            self).get_context_data(**kwargs)
        context['paginator'] = DiggPaginator(self.get_queryset(), 
            self.paginate_by, 
            body=PGN['body'], tail=PGN['tail'], padding=PGN['padding']
            ).page(self.kwargs.get('page', 1))
        return context

class AppraisalParameterCreateView(SuccessMessageMixin, CreateView):
    model = AppraisalParameter
    form_class = AppraisalParameterForm
    success_url = reverse_lazy('appraisal:appraisal_parameter_list')
    template_name = 'administration/appraisal_parameter_form.html'
    success_message = 'Appraisal parameter has been successfully created.'

class AppraisalParameterUpdateView(SuccessMessageMixin, UpdateView):
    model = AppraisalParameter
    form_class = AppraisalParameterForm
    success_url = reverse_lazy('appraisal:appraisal_parameter_list')
    template_name = 'administration/appraisal_parameter_form.html'
    success_message = 'Appraisal parameter has been successfully modified.'
    
class AppraisalParameterDeleteView(DeleteView):
    model = AppraisalParameter
    template_name = 'administration/appraisal_parameter_confirm_delete.html'
    success_url = reverse_lazy('appraisal:appraisal_parameter_list')
    success_message = '"%(name)s" has been successfully deleted.'
    failure_message = '"%(name)s" cannot be deleted because there ' \
        'are records that refer to it.'
    
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        try:
            view = super(AppraisalParameterDeleteView, self).delete(request, 
                *args, **kwargs)
        except IntegrityError as e:
            messages.error(request, self.failure_message % obj.__dict__)
            return reverse('appraisal:appraisal_parameter_list')
        else:
            messages.success(request, self.success_message % obj.__dict__)
            return view
# ===

class AppraisalMeasureListView(ListView):
    model = AppraisalMeasure
    context_object_name = 'appraisal_measure_list'
    paginate_by = 5
    template_name = 'administration/appraisal_measure_list.html'

    def get_context_data(self, **kwargs):
        context = super(AppraisalMeasureListView, 
            self).get_context_data(**kwargs)
        context['paginator'] = DiggPaginator(self.get_queryset(), 
            self.paginate_by, 
            body=PGN['body'], tail=PGN['tail'], padding=PGN['padding']
            ).page(self.kwargs.get('page', 1))
        return context

class AppraisalMeasureCreateView(SuccessMessageMixin, CreateView):
    model = AppraisalMeasure
    form_class = AppraisalMeasureForm
    success_url = reverse_lazy('appraisal:appraisal_measure_list')
    template_name = 'administration/appraisal_measure_form.html'
    success_message = 'The measure has been successfully registered.'

class AppraisalMeasureUpdateView(SuccessMessageMixin, UpdateView):
    model = AppraisalMeasure
    form_class = AppraisalMeasureForm
    success_url = reverse_lazy('appraisal:appraisal_measure_list')
    template_name = 'administration/appraisal_measure_form.html'
    success_message = 'Measure successfully edited.'

class AppraisalMeasureDeleteView(DeleteView):
    model = AppraisalMeasure
    template_name = 'administration/appraisal_measure_confirm_delete.html'
    success_url = reverse_lazy('appraisal:appraisal_measure_list')
    success_message = '"%(definition)s" has been successfully deleted.'
    failure_message = '"%(definition)s" cannot be deleted because there ' \
        'are records that refer to it.'
    
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        try:
            view = super(AppraisalMeasureDeleteView, self).delete(request, 
                *args, **kwargs)
        except IntegrityError as e:
            messages.error(request, self.failure_message % obj.__dict__)
            return reverse('appraisal:appraisal_measure_list')
        else:
            messages.success(request, self.success_message % obj.__dict__)
            return view
