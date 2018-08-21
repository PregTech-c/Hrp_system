import datetime
from urllib.parse import urlencode

from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.template import loader, Context
from django.utils.translation import ugettext as _
from django.views.generic import View, ListView, DeleteView
from django.views.generic.list import MultipleObjectMixin

from django.conf import settings
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages

from easy_pdf.views import PDFTemplateView
from payroll.views import write_pdf

from payroll.models import User, EmployeeProfile, EmployeeDocument, Dependants

from payroll.forms import (EmployeeForm, EmployeeProfileForm,
    ContractualPayForm, EmployeeSearchForm, EmployeeSearchListForm,
    NextOfKinForm, EmployeeDocumentForm, EmployeePhotoForm, StatusForm)


class EmployeeDetailView(View):
    template_name = 'employee_detail.html'

    def get(self, request, *args, **kwargs):
        profile = EmployeeProfile.objects.get(user__id=kwargs.get('pk'))

        docform = EmployeeDocumentForm()

        return render(request, self.template_name,
            {
                'profile': profile,
                'docform': docform,
                'documents': profile.documents.all()
            })

class UploadEmployeePhotoView(View):

    def post(self, request, *args, **kwargs):
        form = EmployeePhotoForm(request.POST, request.FILES)
#        s=ss
        if form.is_valid():
            form.save()
#        messages.success(request, )
        return redirect('payroll:user_detail', pk=kwargs.get('pk'))

class UploadEmployeeDocumentView(View):

    def post(self, request, *args, **kwargs):
        form = EmployeeDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
#        messages.success(request, )
        return redirect('payroll:user_detail', pk=kwargs.get('pk'))

class RemoveEmployeeDocumentView(PermissionRequiredMixin, View):

    permission_required = 'payroll.hrp_manage_employee_info'
    raise_exception = True
    def get(self, request, *args, **kwargs):
        doc = get_object_or_404(EmployeeDocument, pk=kwargs.get('doc_id'))
        doc.delete()
#        messages.success(request, )
        return redirect('payroll:user_detail', pk=kwargs.get('pk'))

class EmployeeListView(ListView):
    template_name = 'employee_list.html'

    context_object_name = 'employee_list'
    paginate_by = 25
    model = User
    def get_queryset(self):
        q = super(EmployeeListView, self).get_queryset()
        emp = self.request.user
        if emp.has_perm('payroll.hrp_manage_employee_info') is False:
            q = q.filter(pk=emp.pk)
        else:
            q = q.filter(
                is_active=True,
                profile__isnull=False
            )

        emp_name = self.request.session.get('emp_name') if \
                self.request.session.get('emp_name') else None
        service_line = self.request.session.get('service_line') if \
                self.request.session.get('service_line') else None
        branch = self.request.session.get('branch') if \
                self.request.session.get('branch') else None


        if emp_name is not None:
            q = q.filter(Q(last_name__icontains=emp_name)|
                        Q(first_name__icontains=emp_name)|
                        Q(profile__other_names__icontains=emp_name)|
                        Q(profile__title__name__icontains=emp_name)
                        )
    #    if service_line is not None:
    #        q = q.filter(profile__service_line__name=service_line)
    #    if branch is not None:
    #        q = q.filter(profile__branch__name=branch)

        return q.order_by('last_name')

    def get_context_data(self, **kwargs):
        context = super(EmployeeListView, self).get_context_data(**kwargs)
        if self.request.session.get('page_message'):
            context['page_message'] = '%s' % self.request.session['page_message']
            self.request.session['page_message'] = ''
        context['form'] = EmployeeSearchListForm
        return context

class EmployeeSendPasswordView(View):
    def get(self, request, *args, **kwargs):
        emp = User.objects.get(pk=kwargs.get('pk'))

        pwd = User.objects.make_random_password(length=6)
        emp.set_password(pwd)
        emp.save()

        self.request.session['page_message'] = "A new password has been sent to {}.".format(
            emp.email)
        email_msg = u"""Hello {},

Below are your authentication details to the Payroll And HR Management portal:

Username: {}
Password: {}

Please note that both username and password are case sensitive.

You may change the password after login.

Management""".format(
                    emp.first_name,
                    emp.username,
                    pwd
                )

        emp.email_user(getattr(settings, 'EMAIL_NOTIFICATION_SUBJECT_TEXT',
                        'HRP Notification'), email_msg,
            from_email=settings.EMAIL_FROM_ADDRESS)
        return redirect('payroll:user_list')

class EmployeeSearchView(View):
    def post(self, request, *args, **kwargs):

        self.request.session['emp_name'] = request.POST['emp_name']
    #    self.request.session['service_line'] = request.POST['service_line']
    #    self.request.session['branch'] = request.POST['branch']

        return redirect('payroll:user_list')

    def get(self, request, *args, **kwargs):
        try:
            del self.request.session['emp_name']
        except: # ignore keyerror
            pass

        return redirect('payroll:user_list')

class EmployeeCreateOrUpdateView(PermissionRequiredMixin, View):

    template_name = 'employee_form.html'
    permission_required = ['payroll.add_employeeprofile',
        'payroll.change_employeeprofile']
    raise_exception = True

    def get(self, request, *args, **kwargs):
        button_text = ''
        try:
#            employee = User.objects.get(pk=1)
            employee = User.objects.get(pk=self.kwargs['pk'])
            uform = EmployeeForm(instance=employee)
            pform = EmployeeProfileForm(instance=employee.profile)
            sform = ContractualPayForm(instance=employee.profile.get_contractual_pay())
            nkinform  = NextOfKinForm(instance=employee.profile.next_of_kin)
        #    dform = StatusForm(instance=employee.profile.status)
            button_text = 'Update'
            action_url = reverse('payroll:user_edit', kwargs={'pk': self.kwargs['pk']})
        except KeyError:
            uform = EmployeeForm()
            pform = EmployeeProfileForm()
            sform = ContractualPayForm()
            nkinform = NextOfKinForm()
    #        dform = StatusForm()
            button_text = 'Add User'
            action_url = reverse('payroll:user_add')

        return render(request,
                    self.template_name,
                    {
                        'uform': uform,
                        'pform': pform,
                        'sform': sform,
            #            'dform': dform,
                        'nkinform': nkinform,
                        'button_text': button_text,
                        'action_url': action_url,
                    }
                )

    def post(self, request, *args, **kwargs):

        if self.kwargs.get('pk'):
            edit = True
            employee = User.objects.get(pk=self.kwargs['pk'])
            pform = EmployeeProfileForm(instance=employee.profile, data=request.POST)
            uform = EmployeeForm(instance=employee, data=request.POST)
            sform = ContractualPayForm(instance=employee.profile.get_contractual_pay(), data=request.POST)
            nkinform = NextOfKinForm(instance=employee.profile.next_of_kin, data=request.POST)
    #        dform = StatusForm(instance=employee.profile.status, data=request.POST)
        else:
            edit = False
            uform = EmployeeForm(data=request.POST)
            pform = EmployeeProfileForm(data=request.POST)
            sform = ContractualPayForm(data=request.POST)
            nkinform = NextOfKinForm(data=request.POST)
    #        dform = StatusForm(data=request.POST)

        if uform.is_valid() and pform.is_valid() \
            and sform.is_valid() and nkinform.is_valid(): #and dform.is_valid():
            user = uform.save()
            uform.save_m2m()
            nkin=nkinform.save()
#            dep=dform.save()

            profile = pform.save(commit=False)

            profile.user = user
            profile.next_of_kin = nkin
#            profile.status = dep
            profile.save()
            pform.save_m2m()

            for skill in pform.cleaned_data['skills']:
                profile.skills.add(skill)
            for cert in pform.cleaned_data['certifications']:
                profile.certifications.add(cert)
            for membership in pform.cleaned_data['memberships']:
                profile.memberships.add(membership)

            salary = sform.save(commit=False)
            salary.employee = user
            salary.save()



            if edit:
                msg = u'%s\'s info has been updated.' %\
                    employee.profile.get_fullname()
                employee.profile.update_unauthorized_payslips()
                if request.POST.get('status') == '0':
                    profile.add_to_unauthorized_payrolls()
            else:
                msg = u'%s %s has been successfully added.' % \
                    (request.POST['first_name'], request.POST['last_name'])
                profile.add_to_unauthorized_payrolls()

            messages.success(request, msg)

            return HttpResponseRedirect(reverse('payroll:user_list'))
        else:
            return render(
                request,
                self.template_name,
                {
                    'uform': uform,
                    'pform': pform,
                    'sform': sform,
                    'nkinform': nkinform,
                    'dform': dform,
                    'button_text': '%s' % ('Update' if self.kwargs.get('pk') else 'Add'),
                    'action_url': reverse('payroll:user_edit',
                        kwargs={'pk':self.kwargs['pk']}) if self.kwargs.get('pk') else reverse('payroll:user_add')

                }
            )

class EmployeeDeleteView(DeleteView):
    model = User #EmployeeProfile
    context_object_name = 'employee'

    def get_success_url(self):
        return reverse('payroll:user_list')
#    success_url = '/user/'

    def get_context_data(self, **kwargs):
        context = super(EmployeeDeleteView, self).get_context_data()
        context.update({
            'employee_name': self.get_object().profile.get_fullname()
        })
        return context

    def delete(self, request, *args, **kwargs):
        employee = self.get_object()
        employee.is_active = False
        employee.save()

        profile = employee.profile
        profile.deleted_on = datetime.datetime.now()
        profile.deleted_by = self.request.user

        profile.save()
        profile.user.payslip_set.filter(
            payroll__authorized_by__isnull=True).delete()

        request.session['page_message'] = '%s has been successfully deleted' % (
            str(self.get_object().profile.get_fullname()))
        return redirect('payroll:user_list')
#        return super(EmployeeDeleteView, self).delete(request, *args, **kwargs)

class EmployeeReportView(ListView):
    template_name = 'employee_report.html'
    queryset = EmployeeProfile.objects.all().order_by('user__last_name')
    context_object_name = 'profile_list'
    paginate_by = 20000

    def get_queryset(self):
        get = self.request.GET.copy()
        self.baseurl = urlencode(get)

        if(len(get)):
            self.form = EmployeeSearchForm(self.request.GET)
        else:
            self.form = EmployeeSearchForm(
                initial = {
                    'bank_field':'on',
                    'service_line_field': 'off',
                    'position_field': 'on',
#                    'acct_no_field': 'on',
#                    'tin_field': 'on',
#                    'nssf_number_field': 'on',
                    'salary_field': 'on',
#                    'status_field': 'on',
                    'employee_number_field': 'on',
                    'email_field': 'on',
                    'phone_number_field': 'on',
#                    'sort_code_field': 'off',
                }
            )

        emp = self.request.user
        if emp.has_perm('payroll.hrp_manage_employee_info') is False:
            qset = Q(pk=emp.profile.pk)
        else:
            qset = Q(user__is_active=True)

        model = EmployeeProfile


        if len(get):
#            qset = Q(deleted_on__isnull=True)
            if get.get('service_line'):
                qset &= Q(service_line=get.get('service_line'))
            if get.get('position'):
                qset &= Q(position=get.get('position'))
            if get.get('bank'):
                qset &= Q(bank=get.get('bank'))
            if get.get('branch'):
                qset &= Q(branch=get.get('branch'))


            return model.objects.filter(qset).order_by('user__last_name')
        else:
            return model.objects.all().order_by('user__last_name')


    def get_context_data(self, **kwargs):
        context = super(EmployeeReportView, self).get_context_data(**kwargs)
        context['form'] = self.form
#        context['status_choices'] = {'0': 'Active', '1': 'Resigned', '2': 'Terminated'}
        get = self.request.GET.copy()

        self.request.session['get'] = ''
#        self.request.session['profile_list'] = ''
        if len(get):
            context['get'] = get
            self.request.session['get'] = get
#            self.request.session['profile_list'] = self.get_queryset()
        context['baseurl'] = reverse('payroll:user_report')
        return context

class EmployeePdfReportView(MultipleObjectMixin, PDFTemplateView):
    template_name = 'employee_pdf_report.html'
    model = EmployeeProfile
    context_object_name = 'profile_list'

    def get_context_data(self, **kwargs):
        self.object_list = self.get_queryset()
        context = super(EmployeePdfReportView, self).get_context_data(**kwargs)
        context.update({
#        'profile_list' : self.get_object_list(),
        'get': self.request.session['get'],
        'num_columns': len(self.request.session['get'])-2,
        'img_path': settings.BASE_DIR + '/payroll/'
        })
        return context

def employee_pdf_view(request):
    import os
    from django.conf import settings
    import urllib

    model = EmployeeProfile


    profile_list = EmployeeProfile.objects.all()

#    payroll = get_object_or_404(Payroll, pk=pk)

    return write_pdf('employee_pdf_report.html',{
        'pagesize' : 'landscape',
#        'payroll' : payroll,
        'profile_list' : profile_list,
        'get': request.session['get'],
        'num_columns': len(request.session['get'])-2})

def employee_csv_view(request):
    import csv

#    response = HttpResponse(mimetype='text/csv')
#    response['content-disposition'] = 'attachment; filename=Employees.csv'

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['content-disposition'] = 'attachment; filename=employees.xls'

    profile_list = EmployeeProfile.objects.all()

    t = loader.get_template('employee_csv_report.html')
    c = Context({
        'profile_list': profile_list,
        'get': request.session['get'],
        'num_columns': len(request.session['get'])-2
    })

    response.write(t.render(c))
    return response


class UserChangePasswordView(View):

    template_name = 'change_password_form.html'

    def get(self, request, *args, **kwargs):

        form = PasswordChangeForm(request.user)

        return render(request, self.template_name, {
            'form': form,
        })

    def post(self, request, *args, **kwargs):

        form = PasswordChangeForm(request.user, request.POST)

        if form.is_valid():
            form.save()

            update_session_auth_hash(request, request.user)
            messages.success(request, _('Password successfully changed.'))
            return redirect('payroll:change_password')
        else:
            return render(request, self.template_name, {
                'form': form,
            })
