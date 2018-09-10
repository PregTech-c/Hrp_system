import csv

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import loader, Context
from django.views.generic.list import MultipleObjectMixin
from django.views.generic import View

from easy_pdf.views import PDFTemplateView

from appraisal.forms import SearchAppraisalReportForm
from appraisal.models import EmployeeAppraisal

class PreformanceSummaryReport(View):
    template_name = 'reports/performance_summary_report.html'
    
    def get(self, request, *args, **kwargs):
        
        appraisal_rpt = request.session.get('appraisal_report')
        emp_appraisals = EmployeeAppraisal.objects.none()
        appraisal_id = None
        initial = {}
        if appraisal_rpt:
            appraisal_id = appraisal_rpt['appraisal_id']
            emp_appraisals = EmployeeAppraisal.objects.filter(
                appraisal__id=appraisal_id)
            initial = {'appraisal': appraisal_id}
#            del request.session['appraisal_report']
            
        context = {
            'form': SearchAppraisalReportForm(
                initial=initial),
            'appraisal_id': appraisal_id,
            'emp_appraisals': emp_appraisals
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = SearchAppraisalReportForm(request.POST)
        
        if form.is_valid():
            request.session['appraisal_report'] = {
                'appraisal_id': form.cleaned_data['appraisal'].id
            }
            return redirect('appraisal:performance_summary')
        else:
            context = {
                'form': form,
            }
        return render(request, self.template_name, context)

class PerformanceSummaryPdfReportView(MultipleObjectMixin, PDFTemplateView):
    template_name = 'reports/performance_summary_pdf.html'
    model = EmployeeAppraisal
    context_object_name = 'emp_appraisals'
    
    def get_queryset(self):
        qs = super(PerformanceSummaryPdfReportView, self).get_queryset()
        return qs.filter(appraisal_id=self.kwargs.get('appraisal_id'))
    
    def get_context_data(self, **kwargs):
        self.object_list = self.get_queryset()
        context = super(PerformanceSummaryPdfReportView, 
            self).get_context_data(**kwargs)
        context.update({
#        'profile_list' : self.get_object_list(),
#        'emp_appraisals': self.get_queryset, #EmployeeAppraisal.objects.get(
#            id=kwargs.get('emp_appraisal_id')),
        'img_path': settings.BASE_DIR + '/payroll/'
        })
        return context

class PerformanceSummaryPdfReportView(View):
    template_name = 'reports/performance_summary_csv.html'
    def get(self, request, *args, **kwargs):

        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['content-disposition'] = 'attachment; filename=performance_summary.xls'

        emp_appraisals = EmployeeAppraisal.objects.filter(
            appraisal_id=kwargs.get('appraisal_id'))

        t = loader.get_template(self.template_name)
#        c = Context({
#            'emp_appraisals': emp_appraisals,
#        })

        response.write(t.render({'emp_appraisals': emp_appraisals}))
        return response
