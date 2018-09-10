__author__ = "Steven Kawuma <kawuma@gmail.com>"
__date__ = "Feb 22, 2017 4:43:22 AM"
from django.contrib.auth.models import User
from django.views.generic import View, ListView, DetailView
from django.shortcuts import redirect, render
from ..conf import settings

from leave.models import LeaveType, LeaveRequest
from leave.forms import OnLeaveReportForm, EmployeeLeaveDaysForm

from django.utils import timezone
from digg_paginator import DiggPaginator

from easy_pdf.views import PDFTemplateView

import datetime

PGN = {'body': 10, 'padding': 1, 'tail': 5, 'padding': 2}

class OnLeaveReportView(ListView):
    
    template_name = 'reports/on_leave.html'
    context_object_name = "leave_request_list"
    paginate_by = 5
    category = ''
    page_message = ''
    
    def post(self, request, *args, **kwargs):
        form = OnLeaveReportForm(request.POST)
        if form.is_valid():
            request.session['rpt_start_date'] = form.data['start_date'] 
            request.session['rpt_end_date'] = form.data['end_date'] 
            request.session['employee_profile'] = form.data['employee'] 
            request.session['search'] = True
            return redirect('leave:leave_report_on_leave', search='on', 
                show_form='on')
        else:
            context = {
                'form': form,
                'show_form': True if self.kwargs.get('show_form') == 'on' else \
                    False,
                'now': timezone.now(),
                'page_message': self.page_message,
                'paginator': DiggPaginator(self.get_queryset(), 
                    self.paginate_by, body=PGN['body'], tail=PGN['tail'], padding=PGN['padding']
                    ).page(self.kwargs.get('page', 1))
            }
            return render(self.request, self.template_name, context=context)
            
    def get_queryset(self):
        
        if self.kwargs.get('search') == 'off':
            try:
                del self.request.session['rpt_start_date']
                del self.request.session['rpt_end_date']
                del self.request.session['search']
            except Exception as e:
                pass
            
        query = LeaveRequest.objects.filter(
            messages__leave_status__in=['A']
            ).distinct().order_by('start_date')
        
        if self.request.session.get('search') is True:
            
            s_date = self.request.session.get('rpt_start_date')
            e_date = self.request.session.get('rpt_end_date')
            profile = self.request.session.get('employee_profile')
            if profile:
                query = query.filter(profile=profile)
            
            try:
                start_date = datetime.datetime.strptime(s_date, 
                '%Y-%m-%d').date()
            except ValueError as e:
                start_date = None
            
            try:
                end_date = datetime.datetime.strptime(e_date, '%Y-%m-%d').date()
            except ValueError as e:
                start_date = None

            if start_date is None or end_date is None:
                arr = []
                now_date = timezone.now().date()
                for r in query:
                    if r.start_date <= now_date <= r.end_date:
                        arr.append(r)
                self.page_message = 'Employees currently on leave'
                return query.filter(pk__in=[r.pk for r in arr])
            
            d = start_date
            arr = []
            while(d < end_date):
                for r in query:
                    if r.start_date <= d <= r.end_date:
                        arr.append(r)
                        continue
                d += datetime.timedelta(1)
            self.page_message = 'On leave between {} and {}.'.format(
                start_date, end_date)
        else:
            arr = []
            now_date = timezone.now().date()
            for r in query:
                if r.start_date <= now_date <= r.end_date:
                    arr.append(r)
            self.page_message = 'Employees currently on leave'
        
        on_leave_list = [r.pk for r in arr]
        self.request.session['on_leave_list'] = on_leave_list
        query = query.filter(pk__in=on_leave_list)
        return query
    
    def get_context_data(self, **kwargs):
        
        context = super(OnLeaveReportView, self).get_context_data(**kwargs)

        additional_context= {
            'form': OnLeaveReportForm(),
            'show_form': True if self.kwargs.get('show_form') == 'on' else False,
            'now': timezone.now(),
            'page_message': self.page_message,
            'paginator': DiggPaginator(self.get_queryset(), 
                self.paginate_by, body=PGN['body'], tail=PGN['tail'], padding=PGN['padding']
                ).page(self.kwargs.get('page', 1))
        }
        context.update(additional_context)
#        self.request.session['on_leave_list'] = list(context['object_list'])
        self.request.session['page_message'] = self.page_message
        
        return context

class OnLeavePdfReportView(PDFTemplateView):
    template_name = "reports/on_leave_pdf.html"
    download_filename = "OnLeave.pdf"
    
    def get_context_data(self, **kwargs):
        
        context = super(OnLeavePdfReportView, self).get_context_data(**kwargs)
        additional_context= {
            'now': timezone.now(),
            'page_message': self.request.session['page_message'],
            'leave_request_list': LeaveRequest.objects.filter(
                pk__in=self.request.session['on_leave_list']),
            'now_date': timezone.now(),
            'logo_path': settings.LOGO_PATH,
        }
        context.update(additional_context)
        return context

class LeaveRequestPdfDetailView(PDFTemplateView):
    template_name = "leave/leaverequest_detail_pdf.html"
    context_object_name = "leaverequest"
    model = LeaveRequest
    download_filename = ":eaveReport.pdf"
    
    def get_context_data(self, **kwargs):
        
        context = super(LeaveRequestPdfDetailView, self).get_context_data(
            pagesize='A4', title="Leave Detail Report", **kwargs)
        additional_context= {
            'leaverequest': LeaveRequest.objects.get(pk=kwargs.get('pk')),
            'logo_path': settings.LOGO_PATH,
            'page_message': self.request.session['page_message'],
            'now_date': timezone.now(),
            'pagesize': "letter landscape"
        }
        context.update(additional_context)
        return context
    
    
class LeaveRequestDetailView(DetailView):
    model = LeaveRequest

class EmployeeLeaveDaysReport(ListView):
    template_name = 'reports/employee_leave_days.html'
#    model = LeaveType
    paginate_by = 5
    context_list_name = 'type_list'
    page_message = ''
    
    def get_queryset(self):
        if self.kwargs.get('search') == 'off':
            try:
                del self.request.session['leave_period_id']
                del self.request.session['user_id']
            except Exception as e:
                pass            

        leave_period_id = self.request.session.get('leave_period_id')
        user_id = self.request.session.get('user_id')

        type_list = []
        if leave_period_id:
            user = User.objects.get(pk=user_id)
            qs = LeaveType.objects.user_types(user=user)
            for t in qs:
                days_left = t.count_no_of_days_left(profile=user.profile, 
                    leave_period_id=leave_period_id)
                t.days_taken = t.no_of_days - days_left
                t.days_carried_forward = t.get_days_carried_forward(
                    profile=user.profile)
                t.days_left = days_left + t.days_carried_forward
                type_list.append(t)

        return type_list
    
    def get_context_data(self, **kwargs):
        form = EmployeeLeaveDaysForm
        profile = None
        user_id = self.request.session.get('user_id')
        if user_id:
            profile = User.objects.get(pk=user_id).profile
        
        totals = {
            'days_taken': 0,
            'no_of_days': 0,
            'days_carried_forward': 0,
            'days_left': 0,
            'total_assigned': 0
        }
        for t in self.get_queryset():
            totals['no_of_days'] += t.no_of_days
            totals['days_taken'] += t.days_taken
            totals['days_carried_forward'] += t.days_carried_forward
            totals['days_left'] += t.days_left
            totals['total_assigned'] += t.no_of_days
            
        context = {
            'form': form,
            'totals': totals,
            'show_form': True if self.kwargs.get('show_form') == 'on' else False,
            'now': timezone.now(),
            'employee_profile': profile, 
            'type_list': self.get_queryset(),

        }
        return context

    def post(self, request, *args, **kwargs):
        form = EmployeeLeaveDaysForm(request.POST)
        if form.is_valid():
            request.session['leave_period_id'] = form.cleaned_data['leave_period'].id
            request.session['user_id'] = form.cleaned_data['employee'].user.id
            
            return redirect('leave:leave_report_days', search='on', 
                show_form='on')
        else:
            context = {
                'form': form,
                'show_form': True if self.kwargs.get('show_form') == 'on' else \
                    False,
                'now': timezone.now(),
            }
            return render(self.request, self.template_name, context=context)

class EmployeeLeaveDaysPdfView(PDFTemplateView):
    template_name = "reports/employee_leave_days_pdf.html"
    download_filename = "LeaveDaysReport.pdf"
    
    def get_context_data(self, **kwargs):

        leave_period_id = self.request.session.get('leave_period_id')
        user_id = self.request.session.get('user_id')
        profile = User.objects.get(pk=user_id).profile

        type_list = []
        totals = {
            'no_of_days': 0,
            'days_taken': 0,
            'days_carried_forward': 0,
            'days_left': 0,
            'total_assigned': 0
        }
        if leave_period_id:
            user = User.objects.get(pk=user_id)
            qs = LeaveType.objects.user_types(user=user)
            for t in qs:
                days_left = t.count_no_of_days_left(profile=user.profile, 
                    leave_period_id=leave_period_id)
                t.days_taken = t.no_of_days - days_left
                t.days_carried_forward = t.get_days_carried_forward(
                    profile=user.profile)
                t.days_left = days_left + t.days_carried_forward
                type_list.append(t)
                
                totals['no_of_days'] += t.no_of_days
                totals['days_taken'] += t.days_taken
                totals['days_carried_forward'] += t.days_carried_forward
                totals['days_left'] += t.days_left
                totals['total_assigned'] += t.no_of_days
                

        context = super(EmployeeLeaveDaysPdfView, self).get_context_data(
            pagesize='A4', title="Leave Days Report", **kwargs)
        additional_context= {
            'type_list': type_list,
            'totals': totals,
            'employee_profile': profile,
            'logo_path': settings.LOGO_PATH,
            'now_date': timezone.now(),
            'pagesize': "letter portrait"
        }
        context.update(additional_context)
        return context
    
