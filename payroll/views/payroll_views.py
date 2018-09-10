import datetime
import calendar
#import urllib2
import logging

from django.http import HttpResponse
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404, get_list_or_404
from django.core.urlresolvers import reverse
from django.core import mail
from django.db.models import Q, Sum
from django.shortcuts import redirect, render
from django.views.generic import *
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import CreateView, UpdateView
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.conf import settings
from django.template import loader, Context

from easy_pdf.views import PDFTemplateView
from digg_paginator import DiggPaginator

from payroll.forms import *
from decimal import Decimal, ROUND_HALF_UP

from payroll.models import *
from payroll.views import write_pdf

logger = logging.getLogger(__name__)

class GeneratePayrollView(ListView):

    model = Payslip
    context_object_name = 'payslip_list'
    paginate_by = 1000
    template_name='payroll_list.html'

    def get_queryset(self):

        try:
            payroll = Payroll.objects.get(pay_period__id=self.kwargs['payperiod_id'])
        except Payroll.DoesNotExist:
            payroll = Payroll()
            payroll.pay_period_id = self.kwargs['payperiod_id']
            payroll.save()

        payroll = Payroll.objects.get(
                        pay_period=self.kwargs['payperiod_id'])

        if self.request.user.has_perm('payroll.hrp_manage_payroll'):

            return Payslip.objects.filter(payroll=payroll,
                                          ).order_by('employee__last_name')
#            return Payslip.objects.filter(payroll=payroll,
#                employee__employeeprofile__id__in=EmployeeProfile.objects.all().values('id')
#                                          ).order_by('employee__last_name')
        else:

            return Payslip.objects.filter(payroll=payroll,
                    employee=self.request.user)

    def get_context_data(self, **kwargs):


        context = super(GeneratePayrollView, self).get_context_data(**kwargs)
        payroll = Payroll.objects.get(pay_period=self.kwargs['payperiod_id'])

        context['form'] = PayslipSearchForm

        context['payroll'] = payroll
        context['can_edit'] = self.request.user.has_perms('payroll.hrp_manage_payroll')
        context['can_authorize'] = self.request.user.has_perms('payroll.hrp_authorize_payroll')
        context['can_send'] = self.request.user.has_perms('payroll.hrp_manage_payroll')

#        context['total_contractual_pay'] = payroll.get_total_contractual_pay(self.request.user)
#        context['total_employee_nssf'] = payroll.get_total_employee_nssf(self.request.user)
#        context['total_msu_nssf'] = payroll.get_total_msu_nssf(self.request.user)
#        context['total_paye'] = payroll.get_total_paye(self.request.user)
#        context['total_deductions'] = payroll.get_total_deductions(self.request.user)
#        context['total_net_pay'] = payroll.get_total_net_pay(self.request.user)
#        context['total_basic_pay'] = payroll.get_total_basic_pay(self.request.user)
#        context['total_outreach_allowance'] = payroll.get_total_outreach_allowance(self.request.user)
#        context['total_allowances'] = payroll.get_total_allowances(self.request.user)
#        context['total_gross_pay'] = payroll.get_total_gross_pay(self.request.user)

        context['payroll_id'] = "%s" % payroll.id
        context['payperiod_id'] = "%s" % self.kwargs['payperiod_id']
        log_message = 'Viewd payroll: %s.' % payroll.pay_period
        Log(user=self.request.user, action=log_message).save()

        return context

class PayrollSearchView(View):
    def post(self, request, *args, **kwargs):

#        self.request.session['branch_id'] = request.POST['branch']
        self.request.session['emp_name'] = request.POST['emp_name']

        return redirect('payroll:payroll_list',
            payperiod_id=kwargs.get('payperiod_id'))

    def get(self, request, *args, **kwargs):
        try:
            del self.request.session['branch_id']
            del self.request.session['emp_name']
        except: # ignore keyerror
            pass

        return redirect('payroll:payroll_list',
            payperiod_id=kwargs.get('payperiod_id'))


## view that shows already generated payrolls
class PayrollView(ListView):

    model = Payslip
    context_object_name = 'payslip_list'
    paginate_by = 1000
    template_name='payroll_list.html'


    def get_queryset(self):

        payroll = Payroll.objects.get(pay_period=self.kwargs['payperiod_id'])
        try:
            # TODO Check permission
            if not payroll.authorized_by and self.kwargs['auth']:
                Payroll.objects.filter(pk=payroll.id
                    ).update(authorized_by=self.request.user,
                        authorized_at=datetime.datetime.now(),
                        total_net_pay=payroll.get_total_net_pay_t(),
                        total_basic_pay=payroll.get_total_basic_pay_t(),
#                        total_outreach_allowance=payroll.get_total_outreach_allowance_t(),
                        total_allowances=payroll.get_total_allowances_t(),
                        total_gross_pay=payroll.get_total_gross_pay_t(),
                        total_employee_nssf=payroll.get_total_employee_nssf_t(),
                        total_msu_nssf=payroll.get_total_msu_nssf_t(),
                        total_paye=payroll.get_total_paye_t(),
                        total_deductions=payroll.get_total_deductions_t(),
                        total_contractual_pay = payroll.get_total_contractual_pay_t()
                        )
#                payroll.total_net_pay = payroll.get_total_net_pay_t()
#                payroll.save()
        except KeyError:
            pass

        if self.request.user.has_perm('payroll.hrp_manage_payroll'):
            emp_name = self.request.session.get('emp_name') if \
                self.request.session.get('emp_name') else None

            q = Payslip.objects.filter(payroll=payroll
                                         ).order_by('employee__last_name')

            msg = ''
#            if branch_id is not None:
#                q = q.filter(employee__profile__branch__id=branch_id)
#                msg = "Branch: %s" % Branch.objects.get(pk=branch_id)
            if emp_name is not None:
                q = q.filter(Q(employee__last_name__icontains=emp_name)|
                                Q(employee__first_name__icontains=emp_name)|
                                Q(employee__profile__other_names__icontains=emp_name))
                msg = "%s Name contains: '%s'" % (msg, emp_name) if msg else "Name: %s" % emp_name

            if msg:
                self.request.session['page_message'] = msg

#            if center_id is not None:
#                q = Payslip.objects.filter(payroll=payroll,
#                                employee__employeeprofile__center__id=center_id,
#                                          ).order_by('employee__last_name')
#            else:
#                q = Payslip.objects.filter(payroll=payroll
#                                          ).order_by('employee__last_name')
            return q
#            return Payslip.objects.filter(payroll=payroll,
#                employee__employeeprofile__id__in=EmployeeProfile.objects.all().values('id')
#                                          ).order_by('employee__last_name')
        else:
            return Payslip.objects.filter(payroll=payroll,
                    employee=self.request.user)

    def get_context_data(self, **kwargs):


        context = super(PayrollView, self).get_context_data(**kwargs)
        payroll = Payroll.objects.get(pay_period=self.kwargs['payperiod_id'])

        context['form'] = PayslipSearchForm
        context['center'] = self.request.session.get('center_id')
        context['emp_name'] = self.request.session.get('emp_name')
        context['payroll'] = payroll
#        context['can_edit'] = self.request.user.has_perms('payroll.hrp_manage_payroll')
#        context['can_authorize'] = self.request.user.has_perms('payroll.hrp_authorize_payroll')
        context['can_send'] = self.request.user.has_perms('payroll.hrp_manage_payroll')

        context['payroll_id'] = "%s" % payroll.id
        context['payperiod_id'] = "%s" % self.kwargs['payperiod_id']
        context['page_message'] = self.request.session.get('page_message')
        log_message = 'Viewd payroll: %s.' % payroll.pay_period
        Log(user=self.request.user, action=log_message).save()

        self.request.session['page_message'] = ''
        return context

class PayrollSummaryReportView(View):

    template_name = 'payroll_summary_report.html'

    def get(self, request, **kwargs):
        form = SearchPayrollForm()

        payroll = self.request.session.get('summary_report_payroll')
        service_line = self.request.session.get('summary_report_service_line')

        if self.request.session.get('summary_report_payroll'):
            form = SearchPayrollForm(initial={'payroll': self.request.session.get('summary_report_payroll')})

            try:
                del self.request.session['summary_report_payroll']
                del self.request.session['service_line']
            except:
                pass

        return render(
            request,
            self.template_name,
            {
                'form': form, #PayrollSummaryReportForm,
                'department': service_line,
                'payroll': payroll,
                'service_line': service_line,
            }
        )

    def post(self, request, *args, **kwargs):
        form = SearchPayrollForm(data=request.POST)
        if form.is_valid():
            if request.POST['payroll']:
                self.request.session['summary_report_payroll'] = Payroll.objects.get(pk=request.POST['payroll'])
                self.request.session['summary_report_service_line'] = (request.POST['service_line'] if \
                        request.POST.get('service_line') else 0)

            return redirect('payroll:payroll_summary_report')
        else:
            return render(
                request,
                'payroll_summary_report.html',
                { 'form': form})

class PayrollSummaryPdfReportView(PDFTemplateView):
    template_name = 'payroll_summary_pdf_report.html'

    def get_context_data(self, **kwargs):
        departments = []
        q = ServiceLine.objects.all()
        if kwargs.get('dept_id') != '0':
            q = q.filter(pk=kwargs.get('dept_id'))

        payroll = get_object_or_404(Payroll, pk=kwargs.get('payroll_id'))
        for department in q:
            sub_total = 0
            q = payroll.payslip_set.filter(employee__profile__service_line=department)
            sub_total = q.aggregate(Sum('net_pay'))['net_pay__sum']
            item = {
                    'name': department.name,
                    'total': sub_total,
                    'totals': q.aggregate(
                                Sum('contractual_pay_amount'),
                                Sum('basic_pay'),
                                Sum('gross_pay'),
                                Sum('paye'),
                                Sum('nssf'),
                                Sum('net_pay'),
                            ),
                    'payslips': q, # payslips.filter(employee__employeeprofile__designation=department),
            }
            departments.append(item)
            item = {}

        allowance_types = AllowanceType.objects.all()
        deduction_types = DeductionType.objects.all()

        allowance_totals = {}
        for allowance_type in allowance_types:
            allowance_totals[allowance_type.name] = PayslipAllowance.objects.filter(payslip__payroll=payroll,allowance_type=allowance_type).aggregate(Sum('amount'))

        allowance_totals = PayslipAllowance.objects.filter(payslip__payroll=payroll).values('allowance_type__name').annotate(sum=Sum('amount'))
        ctx = super(PayrollSummaryPdfReportView, self).get_context_data(**kwargs)
        ctx.update({
            'num_colums': int(allowance_types.count()) + int(deduction_types.count()) + 9,
            'payroll': payroll,
            'payslip_list': payroll.payslip_set.all(),
            'allowance_types': allowance_types,
            'deduction_types': deduction_types,
            'allowance_totals': allowance_totals,
            'departments': departments,
            'img_path': settings.BASE_DIR + '/payroll/',
            'totals': payroll.payslip_set.all().aggregate(
                        Sum('contractual_pay_amount'),
                        Sum('basic_pay'),
                        Sum('gross_pay'),
                        Sum('paye'),
                        Sum('nssf'),
                        Sum('net_pay')
                        )
        })
        return ctx

def payroll_summary_csv_report_view(request, *args, **kwargs):

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['content-disposition'] = 'attachment; filename=payroll_summary_report.xls'

    departments = []
#    q = EmployeeDesignation.objects.all()
    q = ServiceLine.objects.all()
    if kwargs.get('dept_id') != '0':
        q = q.filter(pk=kwargs.get('dept_id'))

    payroll = get_object_or_404(Payroll, pk=kwargs.get('payroll_id'))
    for department in q:
        sub_total = 0
#        q = payroll.payslip_set.filter(employee__profile__designation=department)
        q = payroll.payslip_set.filter(employee__profile__service_line=department)
        sub_total = q.aggregate(Sum('net_pay'))['net_pay__sum']
        item = {
                'name': department.name,
                'total': sub_total,
                'totals': q.aggregate(
                            Sum('contractual_pay_amount'),
                            Sum('basic_pay'),
                            Sum('gross_pay'),
                            Sum('paye'),
                            Sum('nssf'),
                            Sum('net_pay'),
                        ),
                'payslips': q, # payslips.filter(employee__employeeprofile__designation=department),
        }
        departments.append(item)
        item = {}

    payroll = Payroll.objects.get(pk=kwargs.get('payroll_id'))

    t = loader.get_template("payroll_summary_csv_report.html")

    c = Context({
            'payroll': payroll,
            'departments': departments,
            'payslip_list': payroll.payslip_set.all(),
            'allowance_types': AllowanceType.objects.all(),
            'deduction_types': DeductionType.objects.all(),
            'totals': payroll.payslip_set.all().aggregate(
                        Sum('contractual_pay_amount'),
                        Sum('basic_pay'),
                        Sum('gross_pay'),
                        Sum('paye'),
                        Sum('nssf'),
                        Sum('net_pay')
                        ),
        })

    response.write(t.render(c))
    return response


class PayrollCyclesSummaryReportView(ListView):

    context_object_name = 'payroll_list'
    template_name = 'payroll_report.html'

    def get_queryset(self):
        get = self.request.GET.copy()

        if len(get):
            self.form = PayperiodSearchForm(self.request.GET)

            q = Payroll.objects.filter(authorized_at__isnull=False).order_by('-pk')

            if get.get('start_date') and get.get('end_date'):
                q = q.filter(
                    pay_period__start_date__gt=get.get('start_date'),
                    pay_period__end_date__lt=get.get('end_date'),
                    authorized_at__isnull=False
                )
            if get.get('pay_period'):
                q = q.filter(pay_period=get.get('pay_period'))
#            ss
#            if get.get('service_line'):
#                q = q.filter(payslip__in=Payslip.objects.filter(employee__profile__service_line=get.get('sesrvice_line')))

            return q

        else:
            self.form = PayperiodSearchForm(initial={
                    'number_of_staff': 'on',
                    'total_allowances': 'on',
                    'total_paye': 'on',
                    'total_msu_nssf': 'on',
                    'total_deductions': 'on',
                    'total_nssf': 'on',
                    'total_net_pay': 'on',
                    'total_gross_pay': 'on',
                })

        return Payroll.objects.filter(authorized_at__isnull=False)

    def get_context_data(self, **kwargs):
        context = super(PayrollCyclesSummaryReportView, self).get_context_data(**kwargs)
        context['form'] = self.form

        context['get'] = self.request.GET.copy()
        self.request.session['get'] = self.request.GET.copy()

        log_message = 'Opened payroll report search tool.'
        Log(user=self.request.user, action=log_message).save()

        payrolls = self.get_queryset()

        context['totals'] = payrolls.aggregate(
                                Sum('total_gross_pay'),
                                Sum('total_net_pay'),
                                Sum('total_allowances'),
                                Sum('total_deductions'),
                                Sum('total_paye'),
                                Sum('total_msu_nssf'),
                                Sum('total_employee_nssf'),
                                Sum('total_contractual_pay'),
                            )
        return context

class PayrollReportPdfView(PDFTemplateView):
    template_name = 'payroll_pdf_report.html'
    context_object_name = 'payroll_list'

    def get_context_data(self, **kwargs):
        context = super(PayrollReportPdfView, self).get_context_data(**kwargs)
        payroll_list = Payroll.objects.filter(authorized_at__isnull=False
            ).order_by('-pk')

        get = self.request.session['get']
        if get.get('start_date') and get.get('end_date'):
            payroll_list = payroll_list.filter(
                    pay_period__start_date__gt=get.get('start_date'),
                    pay_period__end_date__lt=get.get('end_date')
                )

        if get.get('pay_period'):
            payroll_list = payroll_list.filter(pay_period=get.get('pay_period'))
        context.update({
            'img_path': settings.BASE_DIR + '/payroll/',
            'pagesize': 'A4 landscape',
            'payroll_list': payroll_list,
            'get': get,
            'num_columns': len(get)-1,
            'totals': payroll_list.aggregate(
                            Sum('total_gross_pay'),
                            Sum('total_net_pay'),
                            Sum('total_allowances'),
                            Sum('total_deductions'),
                            Sum('total_paye'),
                            Sum('total_msu_nssf'),
                            Sum('total_employee_nssf'),
                            Sum('total_contractual_pay'),
                        )
        })
        return context

class PayrollReportPdfViewOld(View):

    def get(self, request, *args, **kwargs):
        payroll_list = Payroll.objects.filter(authorized_at__isnull=False).order_by('-pk')

        get = request.session['get']
        if get.get('start_date') and get.get('end_date'):
            payroll_list = payroll_list.filter(
                    pay_period__start_date__gt=kwargs['start_date'],
                    pay_period__end_date__lt=kwargs['end_date']
                )

        if get.get('pay_period'):
            payroll_list = payroll_list.filter(pay_period=get.get('pay_period'))

        return write_pdf(
            'payroll_pdf_report.html',
            {
                'payroll_list': payroll_list,
                'get': request.session['get'],
                'num_columns': len(request.session['get'])-1,
                'totals': payroll_list.aggregate(
                                Sum('total_gross_pay'),
                                Sum('total_net_pay'),
                                Sum('total_allowances'),
                                Sum('total_deductions'),
                                Sum('total_paye'),
                                Sum('total_msu_nssf'),
                                Sum('total_employee_nssf'),
                                Sum('total_contractual_pay'),
                            )
            }
        )

def payroll_csv_report_view(request, *args, **kwargs):
#    import csv
    from django.template import loader, Context

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['content-disposition'] = 'attachment; filename=payroll_summary.xls'

    payroll_list = Payroll.objects.filter(authorized_at__isnull=False).order_by('-pk')

    get = request.session['get']
    if get.get('start_date') and get.get('end_date'):
        payroll_list = payroll_list.filter(
                pay_period__start_date__gt=kwargs['start_date'],
                pay_period__end_date__lt=kwargs['end_date']
            )

    if get.get('pay_period'):
        payroll_list = payroll_list.filter(pay_period=get.get('pay_period'))

    t = loader.get_template('payroll_csv_report.html')
    c = Context({
        'payroll_list': payroll_list,
        'get': request.session['get'],
        'num_columns': len(request.session['get'])-1,
        'totals': payroll_list.aggregate(
                        Sum('total_gross_pay'),
                        Sum('total_net_pay'),
                        Sum('total_allowances'),
                        Sum('total_deductions'),
                        Sum('total_paye'),
                        Sum('total_msu_nssf'),
                        Sum('total_employee_nssf'),
                        Sum('total_contractual_pay'),
                    )
    })
    response.write(t.render(c))
    return response

class PayrollReportExcelView(ListView):
    pass

class PayslipAllowanceView(View):

    template_name = 'allowance_add.html'

    def get(self, request, *args, **kwargs):
        payslip = Payslip.objects.get(pk=kwargs['slip'])
        try:
            PayslipAllowance.objects.get(pk=kwargs['da']).delete()
        except:
            pass
        payslip.update_values()
        allowances = payslip.allowances.all()

        return render(
            request,
            self.template_name,
            {
                'payslip': payslip,
                'allowance_list': allowances,
                'form': PayslipAllowanceForm(
                            initial={'payslip': payslip, 'allowance_type': 1}
                            )
            }
        )

    def post(self, request, *args, **kwargs):

        payslip = Payslip.objects.get(pk=kwargs['slip'])
        allowances = payslip.allowances.all()

        form = PayslipAllowanceForm(data=request.POST)
        if form.is_valid():
            try:
                allowance = PayslipAllowance.objects.get(
                    payslip=request.POST['payslip'],
                    allowance_type=request.POST['allowance_type']
                    # self.fields['allowance_type'].
                )

                PayslipAllowance(
                    id=allowance.id,
                    payslip=payslip,
                    allowance_type=AllowanceType.objects.get(
                        pk=request.POST['allowance_type']),
                    amount=request.POST['amount'],
                    comment=request.POST['comment']).save()
            except PayslipAllowance.DoesNotExist:
                form.save()
            except PayslipAllowance.MultipleObjectsReturned:
                PayslipAllowance.objects.filter(
                    payslip=request.POST['payslip'],
                    allowance_type=request.POST['allowance_type']
                ).delete()
                form.save()

            form = PayslipAllowanceForm(
                            initial={'payslip': payslip, 'allowance_type': 1}
                            )
        else:
            form = PayslipAllowanceForm(data=request.POST,
                        error_class=DivErrorList)

        payslip.update_values()
        return render(
            request,
            self.template_name,
            {
                'payslip': payslip,
                'allowance_list': allowances,
                'form': form
            })

class PayrollSendSlipsView(View):
    def get(self, request, *args, **kwargs):
        from django.core import mail

        payperiod = PayPeriod.objects.get(pk=kwargs.get('payperiod_id'))
        payroll = Payroll.objects.get(pay_period=payperiod) #payperiod.payroll #.payroll #Payroll.objects.get(payroll__pay_period__id=payperiod_id)
        #payslips_to_send = payroll.payslip_set.order_by('id')
        payslips_to_send = payroll.payslip_set.order_by('id')
        emails = []
        for payslip in payslips_to_send: #payroll.payslip_set.all():

            employee = payslip.employee

            from_email = settings.EMAIL_FROM_ADDRESS
            subject = getattr(settings,
                        'EMAIL_NOTIFICATION_SUBJECT_TEXT', 'HRP Notification')
            message = '''Hello {},

Please see your attached payslip for {}.

==
HRP'''.format(
                            employee.profile.get_fullname(),
                            payroll.pay_period
                        )
            email = mail.EmailMessage(
                            subject,
                            message,
                            from_email,
                            [employee.email]
                    )

            url = "{}{}".format(
                getattr(settings, 'HRP_SERVER_URL'),
                reverse('payroll:payslip_pdf_detail',
                    kwargs={'pk': payslip.id})
                )
            req = urllib2.Request(url)
            resp = urllib2.urlopen(req)
            data = resp.read()

            filename = "Payslip for {}.pdf".format(payroll.pay_period)
            email.attach(filename, data)

            emails.append(email)


        connection = mail.get_connection(fail_silently=True)
        connection.send_messages(emails)

        payroll.notified_recipients = True
        payroll.save()

        request.session['page_message'] = 'Payslips have been sent.'
        return redirect('payroll:payroll_list',
            payperiod_id=payperiod.id)

class PayslipSendView(View):

    def get(self, request, *args, **kwargs):

        payslip = Payslip.objects.get(pk=kwargs.get('payslip_id'))

        employee = payslip.employee
        from_email = settings.EMAIL_FROM_ADDRESS
        subject = getattr(settings,
                    'EMAIL_NOTIFICATION_SUBJECT_TEXT', 'HRP Notification')
        message = '''Hello {},

Please see your attached payslip for {}.

--
HRP
'''.format(employee.profile.get_fullname(), payslip.payroll.pay_period)

        email = mail.EmailMessage(
                        subject,
                        message,
                        from_email,
                        [employee.email]
                )
        url = "{}{}".format(
            getattr(settings, 'HRP_SERVER_URL'),
            reverse('payroll:payslip_pdf_detail',
                kwargs={'pk': payslip.id})
            )
        req = urllib2.Request(url)
        resp = urllib2.urlopen(req)
        data = resp.read()

        email.attach('payslip.pdf', data)
        email.send(fail_silently=False)

        messages.success(request, 'The payslip has been sent to {}.'.format(
            request.user.email))
        return redirect('payroll:payslip_detail', pk=payslip.id)

class PayslipDeductionView(View):

    template_name = 'deduction_add.html'

    def get(self, request, *args, **kwargs):
        payslip = Payslip.objects.get(pk=kwargs['slip'])

        if kwargs.get('dd'):
            PayslipDeduction.objects.get(pk=kwargs.get('dd')).delete()
            payslip.update_values()

        deductions = payslip.deductions.all()

        return render(
            request,
            self.template_name,
            {
                'payslip': payslip,
                'deduction_list': deductions,
                'form': PayslipDeductionForm(
                    initial={'payslip': payslip, 'deduction_type': 1}
                )
            })

    def post(self, request, *args, **kwargs):

        payslip = Payslip.objects.get(pk=kwargs['slip'])
        deductions = payslip.deductions.all()

        form = PayslipDeductionForm(data=request.POST)

        if form.is_valid():
            try:
                deduction = PayslipDeduction.objects.get(
                    payslip=request.POST['payslip'],
                    deduction_type=request.POST['deduction_type']
                    # self.fields['allowance_type'].
                )

                PayslipDeduction(
                    id=deduction.id,
                    payslip=payslip,
                    deduction_type=DeductionType.objects.get(
                        pk=request.POST['deduction_type']),
                    amount=request.POST['amount'],
                    comment=request.POST['comment']).save()
            except PayslipDeduction.DoesNotExist:
                form.save()
            except PayslipDeduction.MultipleObjectsReturned:
                PayslipDeduction.objects.filter(
                    payslip=request.POST['payslip'],
                    deduction_type=request.POST['deduction_type']
                ).delete()
                form.save()

            form = PayslipDeductionForm(
                            initial={'payslip': payslip, 'deduction_type': 1}
                            )

            payslip.update_values()
        else:
            form = PayslipDeductionForm(data=request.POST,
                        error_class=DivErrorList)

        return render(
            request,
            self.template_name,
            {
                'payslip': payslip,
                'deduction_list': deductions,
                'form': form
            }
        )

class PayslipTotalDaysWorkedView(UpdateView):
    model = Payslip
    form_class = PayslipTotalDaysWorked

    template_name = 'payslip_days_form.html'
#    payslip = Payslip

    def get_success_url(self):
        payslip = Payslip.objects.get(pk=self.kwargs['pk'])
        payslip.update_values()
        return reverse('payroll:payroll_list', kwargs={'payperiod_id': payslip.payroll.pay_period.id})
#        return reverse('payroll:payslip_days', kwargs={'pk': payslip.id})
#        return '/payroll/%s/' % payslip.payroll.id

    def get_context_data(self, **kwargs):
        context = super(PayslipTotalDaysWorkedView, self).get_context_data(**kwargs)
        payslip = Payslip.objects.get(pk=self.kwargs['pk'])
        context['payperiod_id'] = payslip.payroll.pay_period.id
#        context['w'] = payslip.total_days_worked
#        context['action_url'] = '/payslip/edit/%s/' % self.kwargs['pk']
        return context

    def form_valid(self, form):
        payslip =  Payslip.objects.get(pk=self.kwargs['pk'])
        self.request.session['page_message'] = "%s's work days have been changed to %s." % \
            (payslip.employee.profile.get_fullname(), self.request.POST['total_days_worked'])


        return super(PayslipTotalDaysWorkedView, self).form_valid(form)

class PayslipDetailView(DetailView):

    template_name='payslip_detail.html'
    context_object_name = 'payslip'

    def get_object(self):
        return get_object_or_404(Payslip, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super(PayslipDetailView, self).get_context_data(**kwargs)

#        allowances = []
#        for allowance in self.get_object().allowances.all():
#            allowances = allowances.append(allowance)

#        center = self.employee.profile.center
#
#        if center.is_outreach:
#            daily_allowance = int(center.daily_outreach_allowance)
#            days = self.get_total_days_worked()
#
#            total = total + (days * daily_allowance)

        context['allowances'] = self.get_object().allowances.all()
        context['deductions'] = self.get_object().deductions.all()
        context['profile'] = self.get_object().employee.profile
        return context


def fetch_resources(uri, rel):
    import os
    path = os.path.join(
#            '/Users/steve/NetBeansProjects/Payroll/payroll/static/',
            settings.STATIC_ROOT,
            uri.replace(settings.STATIC_URL, ""),
            ""
        )
    return os.path.join(__file__, uri)
    return path


class PdfPayslipList(PDFTemplateView):
    template_name = 'payroll_pdf.html'

    def get_context_data(self, **kwargs):
        pk = kwargs.get('pk')
        payroll = get_object_or_404(Payroll, pk=pk)
        if self.request.user.has_perm('payroll.hrp_manage_payroll'):
            payslip_list = get_list_or_404(Payslip, payroll=pk)
            payslip_list = payroll.payslip_set.all()
        else:
#            payslip_list = get_list_or_404(Payslip, payroll=pk,
#            employee=self.request.user)
            payslip_list = payroll.payslip_set.filter(employee=self.request.user)

        context = super(PdfPayslipList, self).get_context_data(**kwargs)
        import os
        context.update({
#            'img_path': settings.BASE_DIR + '../payroll',
            'logo_path': settings.LOGO_PATH,
            'payroll' : payroll,
            'payslip_list' : payslip_list,
            'total_basic_pay': payslip_list.aggregate(sum=Sum('basic_pay'))['sum'],
            'total_contractual_pay': payslip_list.aggregate(sum=Sum('contractual_pay__amount'))['sum'],
#            'total_outreach_allowance': payroll.payslip_set.aggregate(sum=Sum('outreach_allowance'))['sum'],
#            'total_allowances': payslip_list.aggregate(sum=Sum('allowances__payslipallowance__amount'))['sum'],
            'total_allowances': payslip_list.aggregate(sum=Sum('allowances__amount'))['sum'],
            'total_gross_pay': payroll.payslip_set.aggregate(sum=Sum('gross_pay'))['sum'],
            'total_employee_nssf': payroll.payslip_set.aggregate(sum=Sum('nssf'))['sum'],
            'total_msu_nssf': payroll.payslip_set.aggregate(sum=Sum('msu_nssf'))['sum'],
            'total_paye': payroll.payslip_set.aggregate(sum=Sum('paye'))['sum'],
#            'total_deductions': payroll.payslip_set.aggregate(sum=Sum('deductions__payslipdeduction__amount'))['sum'],
            'total_deductions': payroll.payslip_set.aggregate(sum=Sum('deductions__amount'))['sum'],
            'total_net_pay': payroll.payslip_set.aggregate(sum=Sum('net_pay'))['sum']

        })
        return context

def payroll_csv_view(request, pk):
    import csv

    response = HttpResponse(content_type='text/csv')
    response['content-disposition'] = 'attachment; filename=payroll.csv'

    payroll = get_object_or_404(Payroll, pk=pk)
#    if request.user.has_perm('payroll.can_view_payroll'):
#        payslip_list = payroll.payslip_set.all()
    if request.user.has_perm('payroll.hrp_manage_payroll'):
        payslip_list = get_list_or_404(Payslip, payroll=pk)
    else:
        payslip_list = get_list_or_404(Payslip, payroll=pk, employee=request.user)

#    payslip_list = Payslip.objects.filter(payroll=pk)
    title = 'Payroll: %s to %s' % (payroll.pay_period.start_date,
                payroll.pay_period.end_date)

    writer = csv.writer(response)
    writer.writerow([title])
    writer.writerow([''])

    writer.writerow([
        'Name',
        'Branch',
        'Contractual Pay',
        'Days Worked',
        'Basic Pay',
        'Other Allowances',
        'Gross Pay',
        'NSSF',
        'Co. NSSF',
        'PAYE',
        'Other Deductions',
        'Net Pay'
        ])

    for payslip in payslip_list:
        profile = payslip.employee.profile
        writer.writerow([
            profile.get_fullname(),
            profile.service_line,
            Decimal(str(payslip.contractual_pay_amount)
                ).quantize(Decimal('0.00'), ROUND_HALF_UP),
            payslip.total_days_worked,
            Decimal(str(payslip.basic_pay)
                ).quantize(Decimal('0.00'), ROUND_HALF_UP),
            Decimal(str(payslip.total_allowances)
                ).quantize(Decimal('0.00'), ROUND_HALF_UP),
            Decimal(str(payslip.gross_pay)
                ).quantize(Decimal('0.00'), ROUND_HALF_UP),
            Decimal(str(payslip.nssf)
                ).quantize(Decimal('0.00'), ROUND_HALF_UP),
            Decimal(str(payslip.msu_nssf)
                ).quantize(Decimal('0.00'), ROUND_HALF_UP),
            Decimal(str(payslip.paye)
                ).quantize(Decimal('0.00'), ROUND_HALF_UP),
            Decimal(str(payslip.total_deduction)
                ).quantize(Decimal('0.00'), ROUND_HALF_UP),
            Decimal(str(payslip.net_pay)
                ).quantize(Decimal('0.00'), ROUND_HALF_UP),
        ])

    writer.writerow([])

    writer.writerow([
        '', '',
        payroll.payslip_set.aggregate(sum=Sum('contractual_pay__amount'))['sum'],
        '',
        payroll.payslip_set.aggregate(sum=Sum('basic_pay'))['sum'],
#        payroll.payslip_set.aggregate(sum=Sum('allowances__payslipallowance__amount'))['sum'],
        payroll.payslip_set.aggregate(sum=Sum('allowances__amount'))['sum'],
        payroll.payslip_set.aggregate(sum=Sum('gross_pay'))['sum'],
        payroll.payslip_set.aggregate(sum=Sum('nssf'))['sum'],
        payroll.payslip_set.aggregate(sum=Sum('msu_nssf'))['sum'],
        payroll.payslip_set.aggregate(sum=Sum('paye'))['sum'],
#        payroll.payslip_set.aggregate(sum=Sum('deductions__payslipdeduction__amount'))['sum'],
        payroll.payslip_set.aggregate(sum=Sum('deductions__amount'))['sum'],
        payroll.payslip_set.aggregate(sum=Sum('net_pay'))['sum']

    ])
    return response

class PayslipFundsSourceView(View):

    template_name = 'payslip_funds_source.html'

    def get(self, request, *args, **kwargs):

        try:
            PayslipFundsSource.objects.get(pk=kwargs['del']).delete()
        except:
            pass

        payslip = Payslip.objects.get(pk=kwargs['slip'])

        sources = payslip.payslipfundssource_set.all()

        return render_to_response(
            self.template_name,
            {
                'payslip': payslip,
                'source_list': sources,
                'form': PayslipFundsSourceForm(
                            initial={'payslip': payslip, 'source': 1}
                            )
            },
            RequestContext(request)
        )

    def post(self, request, *args, **kwargs):

        payslip = Payslip.objects.get(pk=kwargs['slip'])
        sources = payslip.payslipfundssource_set.all()

        form = PayslipFundsSourceForm(data=request.POST)

        if form.is_valid():
            try:
                source = PayslipFundsSource.objects.get(
                    payslip=request.POST['payslip'],
                    source=request.POST['source']
                )

                PayslipFundsSource(
                    id=source.id,
                    payslip=payslip,
                    source=DonorLine.objects.get(pk=request.POST['source']),
                    amount=request.POST['amount']).save()
            except PayslipFundsSource.DoesNotExist:
                form.save()
            except PayslipFundsSource.MultipleObjectsReturned:
                PayslipFundsSource.objects.filter(
                    payslip=request.POST['payslip'],
                    source=request.POST['source']
                ).delete()
                form.save()

            form = PayslipFundsSourceForm(
                            initial={'payslip': payslip, 'source': 1}
                            )
            test = "should save"
        else:
            form = PayslipFundsSourceForm(data=request.POST,
                        error_class=DivErrorList)
            test = "error"
        return render_to_response(
            self.template_name,
            {
                'payslip': payslip,
                'source_list': sources,
                'form': PayslipFundsSourceForm(
                            initial={'payslip': payslip, 'source': 1}
                            ),
                'test': test
            },
            RequestContext(request)
        )

class NssfReportView(View):


    def get(self, request, *args, **kwargs):
        return render(
            request,
            "nssf_report_form.html",
            {
                'form': SearchPayrollForm,
                'test': "test",
                'action_url': reverse('payroll:nssf_report')
            }
        )
#        return render_to_response(
#            "nssf_report_form.html",
#            {
#                'form': SearchPayrollForm,
#                'test': "test",
#                'action_url': reverse('payroll:nssf_report')
#            },
#            RequestContext(request)
#        )

    def post(self, request, *args, **kwargs):

        form = SearchPayrollForm(data=request.POST)

        if form.is_valid():

            payroll = Payroll.objects.get(pk=request.POST['payroll'])
            payslips = payroll.payslip_set.all()
            return render(
                request,
                "nssf_report.html",
                {
                    'payslips': payslips,
                    'payroll': payroll
                }
            )
#            return render_to_response(
#                "nssf_report.html",
#                {
#                    'payslips': payslips,
#                    'payroll': payroll
#                },
#                RequestContext(request)
#            )
#            pass
        else:
            form = SearchPayrollForm(data=request.POST,
                        error_class=DivErrorList)

            return render(
                request,
                "nssf_report_form.html",
                {
                    'form': form,
                    'action_url': reverse('payroll:nssf_report'),
                }
            )
#            return render_to_response(
#                "nssf_report_form.html",
#                {
#                    'form': form,
#                    'action_url': reverse('payroll:nssf_report'),
#                },
#                RequestContext(request)
#            )

class PayeReportView(View):


    def get(self, request, *args, **kwargs):
        return render(
            request,
            "paye_report_form.html",
            {
                'form': SearchPayrollForm,
                'action_url': reverse('payroll:paye_report')
            }
        )
#        return render_to_response(
#            "paye_report_form.html",
#            {
#                'form': SearchPayrollForm,
#                'action_url': reverse('payroll:paye_report')
#            },
#            RequestContext(request)
#        )

    def post(self, request, *args, **kwargs):

        form = SearchPayrollForm(data=request.POST)

        if form.is_valid():

            payroll = Payroll.objects.get(pk=request.POST['payroll'])
            payslips = payroll.payslip_set.all()
            return render(
                request,
                "paye_report.html",
                {
                    'payslips': payslips,
                    'payroll': payroll
                }
            )
        else:
            form = SearchPayrollForm(data=request.POST,
                        error_class=DivErrorList)

            return render(
                request,
                "paye_report_form.html",
                {
                    'form': form,
                    'action_url': reverse('payroll:paye_report'),
                }
            )

def paye_report_csv_view(request, pk):
    import csv

#    response = HttpResponse(mimetype='application/vnd.ms-excel')
#    response['content-disposition'] = 'attachment; filename=paye_report.xls'

    response = HttpResponse(content_type='text/csv')
    response['content-disposition'] = 'attachment; filename=payroll.csv'

    payroll = get_object_or_404(Payroll, pk=pk)

    if request.user.has_perm('payroll.hrp_manage_payroll'):
        payslip_list = get_list_or_404(Payslip, payroll=pk)
    else:
        payslip_list = get_list_or_404(Payslip, payroll=pk, employee=request.user)

    title = 'Co. PAYE: %s to %s' % (payroll.pay_period.start_date,
                payroll.pay_period.end_date)

    writer = csv.writer(response)
    writer.writerow([title])
    writer.writerow([])


    writer.writerow([
                "TIN",
                "Contribution Month",
                "Employee Name",
                "Basic Pay",
                "Gross Pay",
                "PAYE",
        ])

    for payslip in payslip_list:
        profile = payslip.employee.profile
        t = payslip.payroll.date.timetuple()
        writer.writerow([
            profile.tin_number,
            calendar.month_name[t[1]],
            profile.get_fullname(),
            payslip.basic_pay,
            payslip.gross_pay,
            payslip.paye
        ])

    return response

class PayeReportPdfView(PDFTemplateView):
    template_name = 'paye_pdf_report.html'

    def get_context_data(self, **kwargs):
        pk = self.kwargs.get('pk')
        if self.request.user.has_perm('payroll.hrp_manage_payroll'):
            payslip_list = get_list_or_404(Payslip, payroll=pk)
        else:
            payslip_list = get_list_or_404(Payslip, payroll=pk, employee=request.user)

        context = super(PayeReportPdfView, self).get_context_data(**kwargs)
        context.update({
            'pay_period': payslip_list[0].payroll.pay_period,
            'payslip_list': payslip_list,
            'img_path': settings.BASE_DIR + '/payroll/'
        })
        return context

class PayeReportPdfViewOld(View):

    def get(self, request, *args, **kwargs):

#    try:
        pk = self.kwargs.get('pk')
        if request.user.has_perm('payroll.hrp_manage_payroll'):
            payslip_list = get_list_or_404(Payslip, payroll=pk)
        else:
            payslip_list = get_list_or_404(Payslip, payroll=pk, employee=request.user)

        return write_pdf(
            'paye_pdf_report.html',
            {
                'pay_period': payslip_list[0].payroll.pay_period,
                'payslip_list': payslip_list,
            }
        )

def nssf_report_csv_view(request, pk):
    import csv

    response = HttpResponse(content_type='text/csv')
    response['content-disposition'] = 'attachment; filename=nssf_report1.csv'

#    response = HttpResponse(mimetype='application/vnd.ms-excel')
#    response['content-disposition'] = 'attachment; filename=nssf_report.xls'

    payroll = get_object_or_404(Payroll, pk=pk)

    if request.user.has_perm('payroll.hrp_manage_payroll'):
        payslip_list = get_list_or_404(Payslip, payroll=pk)
    else:
        payslip_list = get_list_or_404(Payslip, payroll=pk, employee=request.user)

    title = 'Co. NSSF: %s to %s' % (payroll.pay_period.start_date,
                payroll.pay_period.end_date)

    writer = csv.writer(response)
    writer.writerow([title])
    writer.writerow([''])


    writer.writerow([

                "NSSF Number",
                "Contribution Month",
                "Employee Name",
                "Employee Gross Pay",
                "Employee Contribution",
                "Employer Contribution",
                "Total Contribution"
        ])

    for payslip in payslip_list:
        profile = payslip.employee.profile
        t = payslip.payroll.date.timetuple()
        writer.writerow([
            profile.nssf_number,
            calendar.month_name[t[1]],
            profile.get_fullname(),
            payslip.get_gross_pay(),
            payslip.get_employee_nssf(),
            payslip.get_msu_nssf(),
            payslip.get_msu_nssf() + payslip.get_employee_nssf(),
        ])

    return response

class NssfReportPdfView(PDFTemplateView):
    template_name = 'nssf_pdf_report.html'

    def get_context_data(self, **kwargs):
        pk = self.kwargs.get('pk')
        if self.request.user.has_perm('payroll.hrp_manage_payroll'):
            payslip_list = get_list_or_404(Payslip, payroll=pk)
        else:
            payslip_list = get_list_or_404(Payslip, payroll=pk, employee=request.user)
        context = super(NssfReportPdfView, self).get_context_data(**kwargs)
        context.update({
            'pay_period': payslip_list[0].payroll.pay_period,
            'payslip_list': payslip_list,
            'img_path': settings.BASE_DIR + '/payroll/'
        })
        return context

class BankReportView(View):

#    action_url = "/report/bank/"

    def get(self, request, *args, **kwargs):

        return render(
            request,
            'bank_report_form.html',
            {
                "form": SearchPayrollForm,
                "action_url": reverse('payroll:bank_report')
            }
        )

    def post(self, request, *args, **kwargs):

        form = SearchPayrollForm(data=request.POST)
        if form.is_valid():

            payroll = Payroll.objects.get(pk=request.POST['payroll'])

            if not request.POST['bank']:
                payslips = payroll.payslip_set.filter(employee__in=EmployeeProfile.objects.values('user_id'))
            else:
                payslips = payroll.payslip_set.filter(
                    employee__profile__bank=request.POST['bank'])

            if request.POST['department']:
                payslips = payslips.filter(employee__profile__service_line=request.POST['department'])

            departments = []
            if request.POST.get('categorize'):
                q = ServiceLine.objects.all()
                if request.POST.get('department'):
                    q = q.filter(pk=request.POST.get('department'))

                for department in q:
                    sub_total = 0
                    q = payslips.filter(employee__profile__service_line=department)
                    sub_total = q.aggregate(Sum('net_pay'))['net_pay__sum']
#                    for p in q:
#                        sub_total = sub_total + p.get_net_pay()
                    item = {
                            'name': department.name,
                            'total': sub_total,
                            'payslips': q, # payslips.filter(employee__employeeprofile__designation=department),
                    }
                    departments.append(item)
                    item = {}

#            for payslip in payslips:
#                total_pay += payslip.get_net_pay()
#            from django.forms.models import model_to_dict
#            django.core.serializers.json.DjangoJSONEncoder
            from django.core import serializers
            bank_report_context_data = {
                    'payslips': payslips, #serializers.serialize('json', payslips), #[model_to_dict(p) for p in payslips],
                    'payroll':  payroll,
                    'categorize': request.POST.get('categorize'),
#                    'total_pay': serializers.serialize('json', payslips.aggregate(Sum('net_pay'))['net_pay__sum']),
                    'total_pay': payslips.aggregate(Sum('net_pay'))['net_pay__sum'],
                    'bank': request.POST['bank'],
                    'departments': departments,
                    'selected_department': request.POST.get('service_line'),
                }

            # to be used in PDF & CSV
            request.session['bank_report_context_data'] = bank_report_context_data


            return render(
                request,
                "bank_report.html",
#                {'paroll': 'payroll'}
                bank_report_context_data
            )
        else:
            form = SearchPayrollForm(data=request.POST,
                        error_class=DivErrorList)

            return render(
                request,
                "bank_report_form.html",
                {
                    'form': form,
                    'action_url': reverse('payroll:bank_report'),
                }
            )

def bank_report_csv_view(request, pk):
    import csv
    from django.template import loader, Context

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['content-disposition'] = 'attachment; filename=bank.xls'

    t = loader.get_template('bank_csv_report.html')
    c = Context(request.session['bank_report_context_data'])

    response.write(t.render(c))
    return response

    response = HttpResponse(content_type='text/csv')
    response['content-disposition'] = 'attachment; filename=bank.csv'

#    response = HttpResponse(mimetype='application/vnd.ms-excel')
#    response['content-disposition'] = 'attachment; filename=bank_report.xls'

    payroll = get_object_or_404(Payroll, pk=pk)
    bank=0
    if not bank:
        payslips = payroll.payslip_set.all()
    else:
        payslips = payroll.payslip_set.filter(
            employee__profile__bank=bank)

    total_pay = 0
    for payslip in payslips:
        total_pay += payslip.get_net_pay()


    writer = csv.writer(response)
    writer.writerow([
                'No. Acc.',
                'Debit Amount (UGX)',
                'Account to be Debited',
                'Total Amount'
    ])
    writer.writerow([
                0,
                total_pay,
                0,
                total_pay,
    ])

    writer.writerow([

                "SNo",
                "Employee Name",
                "Bank",
                "Sort Code",
                "Account Numbers",
                "Net Pay",
        ])

    for payslip in payslips:
        profile = payslip.employee.profile
        writer.writerow([
            profile.employee_number,
            profile.get_fullname(),
            profile.bank,
            profile.bank.sort_code,
            """d %s""" % (profile.bank_account_number,),
            payslip.get_net_pay(),
        ])

    return response

def bank_csv_view(request):
    import csv

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['content-disposition'] = 'attachment; filename=bank.xls'

    t = loader.get_template('bank_csv_report.html')
    c = Context(self.request.session['bank_report_context_data'])

    response.write(t.render(c))
    return response

class BankReportPdfView(SingleObjectMixin, PDFTemplateView):
    template_name = 'bank_pdf_report.html'
    model = PayPeriod

    def get_context_data(self, **kwargs):
        pay_period = self.get_object()
        self.object = pay_period
        context = super(BankReportPdfView, self).get_context_data(**kwargs)

        payslip_list = pay_period.payroll.payslip_set.all()
        if not self.request.user.has_perm('payroll.can_view_payroll'):
            payslip_list = payslip_list.filter(employee=self.request.user)

        context.update({
#            'payroll': self.object.payroll,
            'rpt': self.request.session['bank_report_context_data'],
#            'departments': departments,
#            'pay_period': pay_period,
            'total_pay': payslip_list.aggregate(Sum('net_pay'))['net_pay__sum'],
            'img_path': settings.BASE_DIR + '/payroll/'
        })
        return context

class BankReportPdfViewOld(View):

    def get(self, request, *args, **kwargs):

#        pk = self.kwargs.get('pk')
#        pay_period = Payroll.objects.get(pk=pk).pay_period
#        if request.user.has_perm('payroll.can_view_payroll'):
#            payslip_list = Payslip.objects.filter(payroll=pk)
#        else:
#            payslip_list = get_list_or_404(Payslip, payroll=pk, employee=request.user)
#
#
#        departments = []
#
#        for department in EmployeeDesignation.objects.all():
#            sub_total = 0
#            q = payslip_list.filter(employee__employeeprofile__designation=department)
#            for p in q:
#                sub_total = sub_total + p.get_net_pay()
#            item = {
#                    'name': department.name,
#                    'total': sub_total,
#                    'payslips': q, # payslips.filter(employee__employeeprofile__designation=department),
#            }
#            departments.append(item)
#            item = {}

#
        return write_pdf(
            'bank_pdf_report.html',
                {'payslips': self.request.session['bank_report_context_data']}
        )
#        return write_pdf(
#            'bank_pdf_report.html',
#            {
#                'payslip_list': payslip_list,
#                'total_pay': payslip_list.aggregate(Sum('net_pay'))['net_pay__sum'],
#                'departments': departments,
#                'pay_period': pay_period,
#            }
#        )
class PayslipPdfDetailView(SingleObjectMixin, PDFTemplateView):

    template_name='payslip_pdf_detail.html'
    context_object_name = 'payslip'
    model = Payslip

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context = super(PayslipPdfDetailView, self).get_context_data(**kwargs)

        context['allowances'] = self.object.allowances.all()
        context['deductions'] = self.object.deductions.all()
        context['profile'] = self.object.employee.profile
        context.update({
                'allowances': self.object.allowances.all(),
                'deductions': self.object.deductions.all(),
                'profile': self.object.employee.profile,
                'logo_path': settings.LOGO_PATH,

        })
        return context

class PayrollRequestAuthorizationView(View):

    def get(self, request, *args, **kwargs):

        form  = SendEmailForm(request.user)
        return render(
            request,
            'payroll_send_email.html',
            {
                'form':     form,
                'payroll':  get_object_or_404(Payroll, pk=kwargs.get('payroll_id')),
                'action_url': reverse('payroll:payroll_request_authorize', kwargs={'payroll_id':kwargs.get('payroll_id')})
            }
        )

    def post(self, request, *args, **kwargs):

        form = SendEmailForm(request.user, data=request.POST)

        if form.is_valid():
            form.send_email()
            payroll = get_object_or_404(Payroll, pk=kwargs.get('payroll_id'))
            self.request.session['page_message'] = "Payroll authorization request sent."
            return redirect('payroll:payroll_list', payperiod_id=payroll.pay_period.id)

        return render(
            request,
            'payroll_send_email.html',
            {
                'form': form,
                'payroll': get_object_or_404(Payroll, pk=kwargs.get('payroll_id')),
                'action_url': reverse('payroll:payroll_request_authorize', kwargs={'payroll_id':kwargs.get('payroll_id')})
            }
        )

class EmployeeRecurringAdjustmentListView(SuccessMessageMixin,
    ListView):
    model = EmployeeRecurringAdjustment
    template_name = 'employee_allowance_list.html'
    paginator_class = DiggPaginator
    paginate_by = 5

    def get_queryset(self):
        logger.error("Recurring queryset")
        q = EmployeeRecurringAdjustment.objects.exclude(
            Q(deduction__isnull=True) & Q(allowance__isnull=True)|
            Q(expired_at__date__lt=timezone.now().date())
        )

        user = self.request.user
        if not user.has_perm(
            'payroll.add_employeerecurringadjustment'):
            q = q.filter(employee=user.profile)

        if self.kwargs.get('search_data') == 'off':
            if self.request.session.get('search_criteria'):
                del self.request.session['search_criteria']

        search_criteria = self.request.session.get('search_criteria')
        f = Q()

        if search_criteria:
            adj_type = search_criteria.get('adjustment_type')
            name = search_criteria.get('name')
            if name:
                f = Q(employee__user__first_name__icontains=name)
                f = Q(f|Q(employee__user__last_name__icontains=name))
            if str(adj_type) != "0":
                f = Q(f&Q(adjustment_type=adj_type))

        return q.filter(f).distinct()

    def get_context_data(self, **kwargs):
        search_form = self.kwargs.get('show_adj_search_form', 'off')

        search_data = 'off'
        if self.request.session.get('search_criteria'):
            form = RecurringAdjustmentSearchForm(
                self.request.session.get('search_criteria'))
            search_data = 'on'
            search_form = 'on'
        elif self.request.method == 'POST':
            form = RecurringAdjustmentSearchForm(self.request.POST)
            search_data = 'on'
            search_form = 'on'
        else:
            form = RecurringAdjustmentSearchForm()

        context = super(EmployeeRecurringAdjustmentListView,
            self).get_context_data(**kwargs)
        context.update({
            'search_form': form,
            'show_search_form': search_form,
            'search_data': search_data,
            'pg_url': "/rec-adj/{}/{}/".format(
                search_form,
                search_data),
        })
        return context

    def post(self, request, *args, **kwargs):
        search_form = RecurringAdjustmentSearchForm(request.POST)
        if search_form.is_valid():
            request.session['search_criteria'] = search_form.cleaned_data
        else:
            ctx = self.get_context_data()
            ctx['form'] = form
            ctx['search_data'] = 'on'
            return render(request, self.template_name, ctx)
        return super(EmployeeRecurringAdjustmentListView,
            self).get(request, *args, **kwargs)

class EmployeeRecurringAdjustmentCreateView(SuccessMessageMixin,
    PermissionRequiredMixin, CreateView):
    form_class = RecurringAdjustmentForm
    template_name = 'employee_allowance_form.html'
    permission_required = 'employeearecurringdjustment.add'
    success_url = reverse_lazy('payroll:emp_adj_list')

    def get_form_kwargs(self):
        kwargs = super(EmployeeRecurringAdjustmentCreateView,
            self).get_form_kwargs()
        kwargs['adj_type'] = self.kwargs.get('type')
#        s=s
        return kwargs

    def get_success_message(self, cleaned_data):
        name = cleaned_data['employee'].get_fullname()
        if cleaned_data.get('allowance'):
            msg = "{} allowance has been added to {}.".format(
                cleaned_data['allowance'], name)
        elif cleaned_data.get('deduction'):
            msg = "{} deduction has been added to {}.".format(
                cleaned_data['deduction'],name)
        return msg

class EmployeeRecurringAdjustmentUpdateView(SuccessMessageMixin,
    PermissionRequiredMixin, UpdateView):
    form_class = RecurringAdjustmentForm
    template_name = 'employee_allowance_form.html'
    permission_required = 'employeearecurringdjustment.change'
    success_url = reverse_lazy('payroll:emp_adj_list')
    success_message = "%(name)s's %(adj_type)s recurring allowance has been update."
    def get_object(self):
        return EmployeeRecurringAdjustment.objects.get(pk=self.kwargs.get('pk'))

    def get_form_kwargs(self):
        kwargs = super(EmployeeRecurringAdjustmentUpdateView,
            self).get_form_kwargs()
        kwargs['adj_type'] = self.object.adjustment_type

        return kwargs

    def get_success_message(self, cleaned_data):
        name = cleaned_data['employee'].get_fullname()
        if cleaned_data.get('allowance'):
            adj_type = cleaned_data['allowance']
        elif cleaned_data.get('deduction'):
            adj_type = cleaned_data['deduction']

        return self.success_message % dict(cleaned_data,
            name=name, adj_type=adj_type)

class EmployeeRecurringAdjustmentDeleteView(SuccessMessageMixin,
    PermissionRequiredMixin, DeleteView):
    form_class = RecurringAdjustmentForm
#    template_name = 'employee_allowance_form.html'
    permission_required = 'employeearecurringdjustment.delete'
    success_url = reverse_lazy('payroll:emp_adj_list')
    success_message = "The recurring payslip adjustment has been removed."

    def get_object(self):
        return EmployeeRecurringAdjustment.objects.get(pk=self.kwargs.get('pk'))

    def get_success_url(self):
        messages.success(self.request, self.success_message)
        return self.success_url
