from django.shortcuts import render
from django.views.generic import *
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from digg_paginator import DiggPaginator

from leave.models import *
from leave.forms import *

PGN = {'body': 10, 'padding': 1, 'tail': 5, 'padding': 2}

class HolidayCreateView(CreateView):
    form_class = HolidayForm
    template_name = 'leave/holiday_form.html'

    def get_success_url(self):
        messages.success(self.request,
            '{} has been successfully created.'.format(self.object.name))
        return reverse('leave:holiday_list')

class HolidayListView(ListView):
    model = Holiday
    context_object_name = 'holiday_list'
    paginate_by = 5
    template_name = 'leave/holiday_list.html'

    def get_context_data(self, **kwargs):
        context = super(HolidayListView, self).get_context_data(**kwargs)
        context['paginator'] = DiggPaginator(self.get_queryset(),
            self.paginate_by,
            body=PGN['body'], tail=PGN['tail'], padding=PGN['padding']
            ).page(self.kwargs.get('page', 1))
        return context

class HolidayUpdateView(UpdateView):
    model = Holiday
    form_class = HolidayForm
    template_name = 'leave/holiday_form.html'

    def get_success_url(self):
        messages.success(self.request,
            '{} has been updated.'.format(self.object))
        return reverse('leave:holiday_list')

class HolidayDeleteView(DeleteView):
    model = Holiday
    template_name = 'leave/holiday_confirm_delete.html'

    def get_success_url(self):
        messages.success(self.request,
            '{} has been successfully deleted'.format(self.get_object()))
        return reverse('leave:holiday_list')

class LeavePeriodCreateView(CreateView):
    form_class = LeavePeriodForm
    template_name = 'leave/leave_period_form.html'

    def get_success_url(self):
        messages.success(self.request,
            '{} has been successfully created.'.format(self.object))
        return reverse('leave:leave_period_list')

class LeavePeriodListView(ListView):
    model = LeavePeriod
    context_object_name = 'leave_period_list'
    paginate_by = 10
    template_name = 'leave/leave_period_list.html'

    def get_context_data(self, **kwargs):
        context = super(LeavePeriodListView, self).get_context_data(**kwargs)
        context['paginator'] = DiggPaginator(self.get_queryset(),
            self.paginate_by,
            body=PGN['body'], tail=PGN['tail'], padding=PGN['padding']
            ).page(self.kwargs.get('page', 1))
        return context

class LeavePeriodUpdateView(UpdateView):
    model = LeavePeriod
    form_class = LeavePeriodForm
    template_name = 'leave/leave_period_form.html'

    def get_success_url(self):
        messages.success(self.request,
            '{} has been updated.'.format(self.object))
        return reverse('leave:leave_period_list')

class LeavePeriodDeleteView(DeleteView):
    model = LeavePeriod
    template_name = 'leave/leave_period_confirm_delete.html'

    def get_success_url(self):
        messages.success(self.request,
            '{} has been successfully deleted'.format(self.get_object()))
        return reverse('leave:leave_period_list')

class LeaveTypeCreateView(CreateView):
    form_class = LeaveTypeForm
    template_name = 'leave/leave_type_form.html'

    def get_success_url(self):
        messages.success(self.request,
            '{} has been successfully created.'.format(self.object))
        return reverse('leave:leave_type_list')

class LeaveTypeListView(ListView):
    model = LeaveType
    context_object_name = 'leave_type_list'
    paginate_by = 10
    template_name = 'leave/leave_type_list.html'

    def get_context_data(self, **kwargs):
        context = super(LeaveTypeListView, self).get_context_data(**kwargs)
        context['service_line_count'] = ServiceLine.objects.count()
    #    context['position_count'] = Position.objects.count()
        context['paginator'] = DiggPaginator(self.get_queryset(),
            self.paginate_by,
            body=PGN['body'], tail=PGN['tail'], padding=PGN['padding']
            ).page(self.kwargs.get('page', 1))
        return context


class LeaveTypeUpdateView(UpdateView):
    model = LeaveType
    form_class = LeaveTypeForm
    template_name = 'leave/leave_type_form.html'

    def get_success_url(self):
        messages.success(self.request,
            '{} has been updated.'.format(self.object))
        return reverse('leave:leave_type_list')

class LeaveTypeDeleteView(DeleteView):
    model = LeaveType
    template_name = 'leave/leave_type_confirm_delete.html'

    def get_success_url(self):
        messages.success(self.request,
            '{} has been successfully deleted'.format(self.get_object()))
        return reverse('leave:leave_type_list')

class LeaveApproverView(View):
    form_class = LeaveApproverForm
    template_name = 'leave/leave_approver_list.html'

    def get(self, request, *args, **kwargs):
        rm_pk = kwargs.get('rem_pk')
        try:
            rem_pk = LeaveApprover.objects.get(pk=rm_pk)
            rem_pk.delete()
        except:
            pass

        approvers = LeaveApprover.objects.all()
        form = LeaveApproverForm()
        return render(request, self.template_name,
            {'approver_list': approvers, 'form': form})


    def post(self, request, *args, **kwargs):

        form = LeaveApproverForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, '{} has been added.'.format(
                form.cleaned_data['profile'].get_fullname()))
        return redirect('leave:leave_approvers')
