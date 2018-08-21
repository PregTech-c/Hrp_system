from django.db import IntegrityError
from django.shortcuts import render, render_to_response, redirect
from django.views.generic import *
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin

from payroll.models import *
from payroll.forms import PositionForm


class PositionListView(ListView):
    model = Position
    context_object_name = 'position_list'
    template_name = 'administration/position_list.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(PositionListView, self).get_context_data(**kwargs)
        try:
            if self.request.session['page_message']:
                context['page_message'] = '%s' % self.request.session['page_message']
                self.request.session['page_message'] = ''
        except:
            None
        return context

class PositionCreateView(SuccessMessageMixin, CreateView):
    form_class = PositionForm
    template_name = 'administration/position_form.html'
    success_message = '%(name)s has been successfully created.'
    success_url = reverse_lazy('payroll:position_list')

    def get_context_data(self, **kwargs):
        context = super(PositionCreateView, self).get_context_data(**kwargs)
        context['action'] = 'Add'
        return context

class PositionUpdateView(SuccessMessageMixin, UpdateView):
    model = Position
    form_class = PositionForm
    template_name = 'administration/position_form.html'
    success_message = '%(name)s has been successfully updated.'
    success_url = reverse_lazy('payroll:position_list')

    def get_context_data(self, **kwargs):
        context = super(PositionUpdateView, self).get_context_data(**kwargs)
        context['action'] = 'Edit'
        return context

class PositionDeleteView(DeleteView):
    model = Position
    template_name = 'administration/position_confirm_delete.html'
    success_message = '%(name)s has been successfully deleted'
    failed_message = '%(name)s can not be deleted as it is already assigned.'
    
    def get_success_url(self):
        return reverse('payroll:position_list')

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        try:
            view = super(PositionDeleteView, self).delete(request, *args, **kwargs)
        except IntegrityError as e:
            messages.error(request, self.failed_message % obj.__dict__)
            return redirect('payroll:position_list')
        else:
            messages.success(request, self.success_message % obj.__dict__)
            return view
