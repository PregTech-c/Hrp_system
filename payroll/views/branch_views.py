from django.db import IntegrityError
from django.shortcuts import render, render_to_response, redirect
from django.views.generic import *
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin

from payroll.models import *
from payroll.forms import BranchForm


class BranchListView(ListView):
    model = Branch
    context_object_name = 'branch_list'
    template_name = 'administration/branch_list.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(BranchListView, self).get_context_data(**kwargs)
        try:
            if self.request.session['page_message']:
                context['page_message'] = '%s' % self.request.session['page_message']
                self.request.session['page_message'] = ''
        except:
            None
        return context

class BranchCreateView(SuccessMessageMixin, CreateView):
    form_class = BranchForm
    template_name = 'administration/Branch_form.html'
    success_message = '%(name)s has been successfully created.'
    success_url = reverse_lazy('payroll:branch_list')

    def get_context_data(self, **kwargs):
        context = super(BranchCreateView, self).get_context_data(**kwargs)
        context['action'] = 'Add'
        return context

class BranchUpdateView(SuccessMessageMixin, UpdateView):
    model = Branch
    form_class = BranchForm
    template_name = 'administration/branch_form.html'
    success_message = '%(name)s has been successfully updated.'
    success_url = reverse_lazy('payroll:Branch_list')

    def get_context_data(self, **kwargs):
        context = super(BranchUpdateView, self).get_context_data(**kwargs)
        context['action'] = 'Edit'
        return context

class BranchDeleteView(DeleteView):
    model = Branch
    template_name = 'administration/branch_confirm_delete.html'
    success_message = '%(name)s has been successfully deleted'
    failed_message = '%(name)s can not be deleted as it is already assigned.'

    def get_success_url(self):
        return reverse('payroll:branch_list')

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        try:
            view = super(BranchDeleteView, self).delete(request, *args, **kwargs)
        except IntegrityError as e:
            messages.error(request, self.failed_message % obj.__dict__)
            return redirect('payroll:branch_list')
        else:
            messages.success(request, self.success_message % obj.__dict__)
            return view
