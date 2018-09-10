# Create your views here.
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect 
from django.core.urlresolvers import reverse_lazy
from django.views.generic import *
from django.views.generic.list import MultipleObjectMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from easy_pdf.views import PDFTemplateView
from payroll.forms import *

from payroll.models import *
from digg_paginator import DiggPaginator

import datetime
from django.utils import timezone

@login_required
def home(request):
    try:
        profile = request.user.profile
    except:
        profile = None
        
    notifications = []
    if profile:
        
        pending_appraisals = profile.get_appraisals(status='ongoing')
        if pending_appraisals:
            for emp_appraisal in pending_appraisals:
                notifications.append(
                    '{} <a href="{}">Appraisal</a> ({}) due on {}'.format(
                    'Pending' if emp_appraisal.status == '1' else 'In progress',
                    reverse('appraisal:employee_appraisal_measure_list', 
                        kwargs={'emp_app_id': emp_appraisal.id}),
                    emp_appraisal.appraisal.description,
                    timezone.datetime.strftime(emp_appraisal.appraisal.due_date, 
                        '%m/%d/%Y')))
        
        received_appraisals = profile.get_received_appraisals(status='ongoing')
        if received_appraisals:
            for emp_appraisal in received_appraisals:
                notifications.append(
                    'Received <a href="{}">Appraisal</a> ({}) from {}'.format(
                    reverse('appraisal:received_employee_appraisal_measure_list', 
                        kwargs={'emp_app_id': emp_appraisal.id}),
                        emp_appraisal.appraisal.description,
                        emp_appraisal.employee_profile.get_fullname()
                    ))
        
    return render(request, 'home.html', {'notifications': notifications})

class PayPeriodCreateView(CreateView):
    form_class = PayPeriodForm #(error_class=DivErrorList)
    template_name = 'payperiod_form.html'

    def get_success_url(self):
        return reverse('payroll:payperiod_list')

    def get_context_data(self, **kwargs):
        context = super(PayPeriodCreateView, self).get_context_data(**kwargs)
        context['action_url'] = reverse('payroll:payperiod_add')
        context['page_header'] = "Add Pay Period"
        return context

    def form_valid(self, form):
        log_message = 'Created payperiod: from %s to %s.' % \
            (form.data['start_date'], form.data['start_date'])
        Log(user=self.request.user, action=log_message).save()

        return super(PayPeriodCreateView, self).form_valid(form)

class PayPeriodUpdateView(UpdateView):
    form_class = PayPeriodForm
    template_name = 'payperiod_form.html'

    def get_success_url(self):
        return reverse('payroll:payperiod_list')

    def get_object(self):
        return PayPeriod.objects.get(pk=self.kwargs.get('pk'))

    def get_context_data(self, **kwargs):
        context = super(PayPeriodUpdateView, self).get_context_data(**kwargs)
        context['action_url'] = reverse('payroll:payperiod_edit', kwargs={'pk': context['object'].id})
        context['page_header'] = "Edit Pay Period: %s" % (context['object'])
        return context

    def form_valid(self, form):
        self.request.session['page_message'] = \
            '%s has been successfully edited.' % self.get_object()
        payroll = self.get_object().get_payroll()
            
        view = super(PayPeriodUpdateView, self).form_valid(form)

        for payslip in payroll.payslip_set.all():
            payslip.total_days_worked = self.get_object().total_working_days
            payslip.update_values()

        return view
    
class PayPeriodListView(ListView):
#    model = PayPeriod
    context_object_name = 'pay_period_list'
    paginate_by = 10

    def get_queryset(self):
       Log(user=self.request.user, action='Viewed pay-periods list.').save()
       try:
           delete_period = self.kwargs['del_id']
           pay_period = PayPeriod.objects.get(pk=delete_period)
           self.request.session['page_message'] = "Payperiod %s deleted" % pay_period
           pay_period.delete()
       except:
           pass#    def get_context_data(self, **kwargs):
       if self.request.user.has_perm('payroll.hrp_manage_payroll'):
           return PayPeriod.objects.all()
       else:
           payslip_set = self.request.user.payslip_set.all()
           payroll_set = Payroll.objects.filter(payslip__in=payslip_set)
           return PayPeriod.objects.filter(payroll__in=payroll_set)
           return PayPeriod.objects.all()

    def get_context_data(self, **kwargs):
        context = super(PayPeriodListView, self).get_context_data(**kwargs)
        try:
            context['page_message'] = self.request.session['page_message']
            del self.request.session['page_message']
        except:
            pass
        return context
    
## Begin Banks
class BankListView(ListView):
    model = Bank
    context_object_name = 'bank_list'
    paginate_by = 10
    queryset = Bank.objects.filter().order_by('name')

    def get_context_data(self, **kwargs):
        Log(user=self.request.user, action='Listed saved banks.').save()
        context = super(BankListView, self).get_context_data(**kwargs)
        try:
            if self.request.session['page_message']:
                context['page_message'] = '%s' % self.request.session['page_message']
                self.request.session['page_message'] = ''
        except:
            None
        return context

class BankCreateView(CreateView):
    form_class = BankForm

    template_name = 'bank_form.html'

    def get_success_url(self):
        return reverse('payroll:bank_list')

    def get_context_data(self, **kwargs):
        context = super(BankCreateView, self).get_context_data(**kwargs)
        context['action_url'] = reverse('payroll:bank_add')
        context['page_header'] = "Register a New Bank"
        return context

    def form_valid(self, form):

        log_message = 'Entered a new bank: %s.' % form.data['name']
        Log(user=self.request.user, action=log_message).save()

        self.request.session['page_message'] = \
            '%s has been created' % form.data['name']
        return super(BankCreateView, self).form_valid(form)
    
class BankUpdateView(SuccessMessageMixin, UpdateView):
    model = Bank
    form_class = BankForm
    template_name = 'bank_form.html'
    success_message = "%(name)s has been successfully updated."
    success_url = reverse_lazy('payroll:bank_list')

    def get_context_data(self, **kwargs):
        context = super(BankUpdateView, self).get_context_data(**kwargs)
        context['action'] = "Edit"  # % self.get_object()
        return context

    def form_valid(self, form):
        log_message = 'Edited bank %s.' % form.data['name']
        Log(user=self.request.user, action=log_message).save()

#        self.request.session['page_message'] = '%s has been successfully modified.' % \
#            str(self.get_object())
        return super(BankUpdateView, self).form_valid(form)

class BankDeleteView(DeleteView):
    model = Bank
    success_message = "%(name) has been successfully added."
    failed_message = '%(name)s can not be deleted as it is already assigned.'
    success_url = reverse_lazy('payroll:bank_list')

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        log_message = 'Deleted bank: %s.' % str(self.get_object())
        Log(user=self.request.user, action=log_message).save()

        try:
            view = super(BankDeleteView, self).delete(request, *args, **kwargs)
        except IntegrityError as e:
            messages.error(request, self.failed_message % obj.__dict__)
            return redirect('payroll:bank_list')
        else:
            messages.success(request, self.success_message % obj.__dict__)
            return view
## End Banks

class BankBranchView(ListView):

    context_object_name = "bank_branch_list"
    template_name = "bank_branch_list.html"
    paginate_by = 10
    
    def get_queryset(self):
        return BankBranch.objects.filter(bank__id=self.kwargs.get('bank_id'))

    def get_context_data(self, **kwargs):
        context = super(BankBranchView, self).get_context_data(**kwargs)
        context['bank'] = Bank.objects.get(pk=self.kwargs.get('bank_id'))

        if self.request.session.get('page_message'):
            context['page_message'] = '%s' % self.request.session['page_message']
            self.request.session['page_message'] = ''

        return context

class BankBranchCreateView(SuccessMessageMixin, CreateView):

    model = BankBranch
    form_class = BankBranchForm
    
    def get_initial(self):
        initial = super(BankBranchCreateView, self).get_initial()
        initial = initial.copy()
        initial['bank'] = self.kwargs.get('bank_id')
        return initial

    template_name = 'bank_branch_form.html'

    def get_success_url(self):
        return reverse('payroll:bank_branch_list',
                kwargs={'bank_id': self.kwargs.get('bank_id')})

    def get_context_data(self, **kwargs):
        context = super(BankBranchCreateView, self).get_context_data(**kwargs)
        context['bank'] = Bank.objects.get(pk=self.kwargs.get('bank_id'))
        context['page_header'] = "Register a New %s Branch" % \
                Bank.objects.get(pk=self.kwargs.get('bank_id'))
        context['action_url'] = reverse('payroll:bank_branch_add',
                kwargs={'bank_id': self.kwargs.get('bank_id')})
        return context

    def form_valid(self, form):

        log_message = 'Entered a new branch: %s.' % form.data['branch_name']
        Log(user=self.request.user, action=log_message).save()

        self.request.session['page_message'] = \
            '%s has been created' % form.data['branch_name']
        return super(BankBranchCreateView, self).form_valid(form)

class BankBranchDeleteView(DeleteView):
    model = BankBranch

    def get_success_url(self):
        return reverse('payroll:bank_branch_list',
                kwargs={'bank_id': self.kwargs.get('bank_id') })

    def delete(self, request, *args, **kwargs):

        log_message = 'Deleted %s branch.' % str(self.get_object())
        Log(user=self.request.user, action=log_message).save()

        self.request.session['page_message'] = '%s branch has been deleted.' % \
                str(self.get_object())
        return super(BankBranchDeleteView, self).delete(request, *args, **kwargs)

class BankBranchUpdateView(UpdateView):
    model = BankBranch
    form_class = BankBranchForm
    template_name = 'bank_branch_form.html'

    def get_success_url(self):
        return reverse('payroll:bank_branch_list',
                kwargs={'bank_id': self.get_object().bank.id})

    def get_context_data(self, **kwargs):
        context = super(BankBranchUpdateView, self).get_context_data(**kwargs)
        context['bank'] = self.get_object().bank
        context['page_header'] = "Edit %s" % self.get_object()
        context['action_url'] = reverse('payroll:bank_branch_edit',
            kwargs={'pk':self.get_object().id})
        return context

    def form_valid(self, form):
        log_message = 'Edited branch %s.' % form.data['branch_name']
        Log(user=self.request.user, action=log_message).save()

        self.request.session['page_message'] = '%s branch has been successfully modified.' % \
            str(self.get_object())
        return super(BankBranchUpdateView, self).form_valid(form)

class ActivityListView(ListView):
#    model = Log
    context_object_name = 'log_list'
    template_name = 'activity_list.html'
    paginate_by = 15

    def get_queryset(self, **kwargs):
        if self.request.user.has_perm('payroll.hrp_view_system_reports'):
            queryset = Log.objects.filter().order_by('-id')
        else:
            queryset = Log.objects.filter(user=self.request.user).order_by('-id')

        if self.request.session.get('activity_user_id'):
            queryset = queryset.filter(user__id=self.request.session.get('activity_user_id'))
        if self.request.session.get('activity_end_date') or self.request.session.get('activity_start_date'):    
            if self.request.session.get('activity_end_date'):
                queryset = queryset.filter(time_stamp__lte=self.request.session.get('activity_end_date'))
            if self.request.session.get('activity_start_date'):
                queryset = queryset.filter(time_stamp__gte=self.request.session.get('activity_start_date'))
        else:
            queryset = queryset.filter(time_stamp__month=datetime.datetime.now().month)

        return queryset
    
    def get_context_data(self, **kwargs):
        Log(user=self.request.user, action='Reviewed user system activity.').save()
        context = super(ActivityListView, self).get_context_data(**kwargs)

        if self.request.session.get('activity_form'):
            context['form'] = self.request.session.get('activity_form')
        else:
            context['form'] = UserActivitySearchForm

        context['user_id'] = self.request.session.get('activity_user_id')
        context['start_date'] = self.request.session.get('activity_start_date')
        context['end_date'] = self.request.session.get('activity_end_date')
        
        context['paginator'] = DiggPaginator(self.get_queryset(), 20, 
            body=10, tail=5, padding=3).page(self.kwargs.get('page', 1))

        return context

class ActivityPdfView(MultipleObjectMixin, PDFTemplateView):
    template_name = 'activity_pdf_list.html'
    context_object_name = 'activity_list'
    
    def get_queryset(self):
        if self.request.user.has_perm('payroll.hrp_view_system_reports'):
            q = Log.objects.filter().order_by('-id')
        else:
            q = Log.objects.filter(user=self.request.user).order_by('-id')
        if self.kwargs.get('from') != u'0':
            q = q.filter(time_stamp__gte=self.kwargs.get('from'))

        if self.kwargs.get('to') != u'0':
            q = q.filter(time_stamp__lte=self.kwargs.get('to'))
        return q
    
    def get_context_data(self, *args, **kwargs):
        emp_name = 0
        if kwargs.get('emp') != u'0':
#            q = q.filter(user__id=kwargs.get('emp'))
            emp = User.objects.get(pk=kwargs.get('emp'))
            try:
                emp_name = emp.profile.get_fullname()
            except:
                emp_name = emp
                
        self.object_list = self.get_queryset()
        context = super(ActivityPdfView, self).get_context_data(*args, **kwargs)
        context.update({
            'employee': emp_name,
            'from': kwargs.get('from'),
            'to': kwargs.get('to'),
            'img_path': settings.BASE_DIR + '/payroll/'
        })
        return context
    
class ActivityPDFViewOld(View):

    def get(self, request, *args, **kwargs):

        if self.request.user.has_perm('payroll.hrp_view_system_reports'):
            q = Log.objects.filter().order_by('-id')
        else:
            q = Log.objects.filter(user=self.request.user).order_by('-id')

        emp_name = 0
        if kwargs.get('emp') != u'0':
            q = q.filter(user__id=kwargs.get('emp'))
            emp = User.objects.get(pk=kwargs.get('emp'))
            try:
                emp_name = emp.profile.get_fullname()
            except:
                emp_name = emp

        if kwargs.get('from') != u'0':
            q = q.filter(time_stamp__gte=kwargs.get('from'))

        if kwargs.get('to') != u'0':
            q = q.filter(time_stamp__lte=kwargs.get('to'))

        return write_pdf(
            'activity_pdf_list.html',
            {
                'activity_list': q,
                'employee': emp_name,
                'from': kwargs.get('from'),
                'to': kwargs.get('to'),
            }
            
        )
class UserActivitySearchView(View):

    def post(self, request, *args, **kwargs):

        form = UserActivitySearchForm(request.POST)
        if form.is_valid():
            self.request.session['activity_start_date'] = request.POST['start_date']
            self.request.session['activity_end_date'] = request.POST['end_date']
            self.request.session['activity_user_id'] = request.POST['user']

        self.request.session['activity_form'] = form
        return redirect('payroll:activity_list')

    def get(self, request, *args, **kwargs):
        try:
            del self.request.session['activity_start_date']
            del self.request.session['activity_end_date']
            del self.request.session['activity_form']
        except:
            pass
        
        return redirect('payroll:activity_list')
    
def write_pdf(template_src, context_dict):
    from django import http
    from django.template.loader import get_template
    from django.template import Context
    import ho.pisa as pisa
    import cStringIO as StringIO
    import cgi
    import os
    from django.conf import settings

    template = get_template(template_src)
    context = Context(context_dict)

    html  = template.render(context)
    result = StringIO.StringIO()

    pdf = pisa.pisaDocument(
            StringIO.StringIO(html.encode("UTF-8")),
            result,
            encoding='UTF-8',
            path=__file__,
#            link_callback=fetch_resources
        )

    if not pdf.err:
        return http.HttpResponse(result.getvalue(), \
             content_type='application/pdf')

    return http.HttpResponse('Gremlins ate your pdf! %s' % cgi.escape(html))

