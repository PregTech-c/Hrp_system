__author__ = "Steven Kawuma <kawuma@gmail.com>"
__date__ = "Jan 31, 2017 3:48:26 PM"

from django.contrib import messages
from django.views.generic import *
from django.core.urlresolvers import reverse

from payroll.models.employee_models import Nationality
from payroll.forms.employee_forms import NationalityForm
from digg_paginator import DiggPaginator

PGN = {'body': 10, 'padding': 1, 'tail': 5, 'padding': 2}

class NationalityListView(ListView):
    model = Nationality
    context_object_name = 'nationality_list'
    paginate_by = 10
    template_name = 'administration/nationality_list.html'

    def get_context_data(self, **kwargs):
        context = super(NationalityListView, self).get_context_data(**kwargs)
        context['paginator'] = DiggPaginator(self.get_queryset(), 
            self.paginate_by, 
            body=PGN['body'], tail=PGN['tail'], padding=PGN['padding']
            ).page(self.kwargs.get('page', 1))
        return context
    
class NationalityCreateView(CreateView):
    
    model = Nationality
    form_class = NationalityForm
    template_name = 'administration/nationality_form.html'
    
    def get_success_url(self):
        ss=s
        messages.success(self.request, 
            '{} has been successfully created.'.format(self.object.name))
        return reverse('payroll:nat_list')

class NationalityUpdateView(UpdateView):
    model = Nationality
    form_class = NationalityForm
    template_name = 'administration/nationality_form.html'

    def get_success_url(self):
        messages.success(self.request,
            '{} has been updated.'.format(self.object))
        return reverse('payroll:nat_list')

class NationalityDeleteView(DeleteView):
    model = Nationality
    template_name = 'administration/nationality_confirm_delete.html'

    def get_success_url(self):
        messages.success(self.request,
            '{} has been successfully deleted'.format(self.get_object()))
        return reverse('payroll:nat_list')
