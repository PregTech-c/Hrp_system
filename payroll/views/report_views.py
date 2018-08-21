from django.shortcuts import get_object_or_404
from django.views.generic import View, ListView
from django.db.models import Sum
from django.views.generic.detail import SingleObjectMixin

from payroll.forms import SalaryHistoryForm
from payroll.models import ContractualPay, Log, User, Payslip, EmployeeProfile
from payroll.views import write_pdf
from easy_pdf.views import PDFTemplateView

class SalaryProgressionView(ListView):

    template_name = 'salary_progression_report_form.html'
    context_object_name = 'payslips'

    def get_queryset(self):
        get = self.request.GET.copy()

        self.form = SalaryHistoryForm
        q = Payslip.objects.filter(id=-1)

        if len(get):
            self.form = SalaryHistoryForm(self.request.GET)
            if get.get('employee'):
                profile = get_object_or_404(EmployeeProfile, pk=get.get('employee'))
                q = profile.user.payslip_set.filter(payroll__authorized_at__isnull=False
                    ).order_by('-payroll__authorized_at')
                if get.get('start_date') and get.get('end_date'):
               	    q = q.filter(
                    payroll__pay_period__start_date__gt=get.get('start_date'),
                    payroll__pay_period__start_date__lt=get.get('end_date'),
                    )
        return q
    
    def get_context_data(self, **kwargs):
        context = super(SalaryProgressionView, self).get_context_data(**kwargs)
        context['form'] = self.form
        context['get'] = self.request.GET.copy()
        self.request.session['get'] = self.request.GET.copy()

        q = self.get_queryset()
        if q is not None:
            context['total_contractual_pay'] = q.aggregate(Sum('contractual_pay__amount'))['contractual_pay__amount__sum']
            context['total_basic_pay'] = q.aggregate(Sum('basic_pay'))['basic_pay__sum']
            context['total_net_pay'] = q.aggregate(Sum('net_pay'))['net_pay__sum']
            context['total_gross_pay'] = q.aggregate(Sum('gross_pay'))['gross_pay__sum']
            context['total_nssf'] = q.aggregate(Sum('nssf'))['nssf__sum']
            context['total_paye'] = q.aggregate(Sum('paye'))['paye__sum']

        log_message = 'Opened payroll salary history report search tool.'
        Log(user=self.request.user, action=log_message).save()

        return context

class SalaryProgressionPdfReportView(SingleObjectMixin, PDFTemplateView):
    template_name = 'salary_progression_report.html'
    model = EmployeeProfile
    context_object_name = 'employee_profile'
    
    def get_context_data(self, *args, **kwargs):
        from_date = kwargs.get('from')
        to_date = kwargs.get('to')
        self.object = self.get_object()
        q = self.object.user.payslip_set.all()
        if from_date != u'0':
            q = q.filter(payroll__pay_period__start_date__gte=from_date)
        if to_date != u'0':
            q = q.filter(payroll__pay_period__start_date__lte=to_date)
        q = q.order_by('payroll__pay_period__start_date')
        
        self.object = self.get_object()
        context = super(SalaryProgressionPdfReportView, self).get_context_data(*args, **kwargs)
        context.update({
            'total_contractual_pay': q.aggregate(Sum('contractual_pay__amount'))['contractual_pay__amount__sum'],
            'total_basic_pay': q.aggregate(Sum('basic_pay'))['basic_pay__sum'],
            'total_net_pay': q.aggregate(Sum('net_pay'))['net_pay__sum'],
            'total_gross_pay': q.aggregate(Sum('gross_pay'))['gross_pay__sum'],
            'total_nssf': q.aggregate(Sum('nssf'))['nssf__sum'],
            'total_paye': q.aggregate(Sum('paye'))['paye__sum'],
            'payslip_list': q,
        })
        return context
    