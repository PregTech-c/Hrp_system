from django.conf.urls import url
from django.conf import settings
from django.contrib.auth import views as auth_views
from payroll.views import *
#from payroll.branches import *

from .qualification_urls import qualification_patterns
from .employee_urls import employee_patterns
from .administration_urls import administration_patterns

urlpatterns = [

    url('^$', home, name='home1'),
    url('^index.*/$', home, name='index'),
    url('^home.*/$', home, name='home'),
    url('^login/', auth_views.login,
             {'template_name': 'login.html'}, name='login'),
    url('^logout/', auth_views.logout,
            {'next_page': settings.LOGIN_URL }, name='logout'),

    url('^bank/$', BankListView.as_view(), name="bank_list"),
    url('^bank/page(?P<page>[0-9]+)/$', BankListView.as_view(),
        name="bank_list_p"),
    url('^bank/new/', BankCreateView.as_view(), name='bank_add'),
    url('^bank/edit/(?P<pk>\d+)/$', BankUpdateView.as_view(), name='bank_edit'),
    url('^bank/delete/$', BankDeleteView.as_view(), name='bank_delete_old'),
    url('^bank/delete/(?P<pk>\d+)/$', BankDeleteView.as_view(),
        name='bank_delete'),
    url('^bankbranch/(?P<bank_id>\d+)/$', BankBranchView.as_view(), name='bank_branch_list'),
    url('^bankbranch/new/(?P<bank_id>\d+)/$', BankBranchCreateView.as_view(), name='bank_branch_add'),
    url('^bankbranch/edit/(?P<pk>\d+)/$', BankBranchUpdateView.as_view(), name='bank_branch_edit'),
    url('^bankbranch/delete/(?P<bank_id>\d+)/(?P<pk>\d+)/$', BankBranchDeleteView.as_view(),
        name='bank_branch_delete'),

    url('^activity/$', ActivityListView.as_view(), name='activity_list'),
    url('^activity/search/$', UserActivitySearchView.as_view(), name='activity_search'),
    url('^activity/page(?P<page>[0-9]+)/$', ActivityListView.as_view(),
        name='activity_list_p'),
    url('^activity/pdf/(?P<emp>\d+)/(?P<from>.+)/(?P<to>.+)/$',
        ActivityPdfView.as_view(), name='activity_pdf_list'),
#    url('^activity/pdf/(?P<emp>\d+)/(?P<from>.+)/(?P<to>.+)/$', ActivityPDFView.as_view(), name='activity_pdf_list'),

    url('^payperiod/$', PayPeriodListView.as_view(), name='payperiod_list'),
    url('^payperiod/page(?P<page>[0-9]+)/$', PayPeriodListView.as_view(),
        name='payperiod_list_p'),
    url('^payperiod/add/$', PayPeriodCreateView.as_view(),
        name='payperiod_add'),
    url('^payperiod/edit/(?P<pk>\d+)/$', PayPeriodUpdateView.as_view(),
        name='payperiod_edit'),
    url('^payperiod/del(?P<del_id>\d+)/$', PayPeriodListView.as_view(),
        name='payperiod_del'),

    url('^payroll/(?P<payperiod_id>\d+)/$', PayrollView.as_view(),
        name='payroll_list'),
    url('^payroll/(?P<payperiod_id>\d+)/page(?P<page>[0-9]+)/$', PayrollView.as_view(),
        name='payroll_list_p'),
    url('^payroll/search/(?P<payperiod_id>\d+)/$', PayrollSearchView.as_view(),
        name='payroll_search'),

    url('^payroll/new/(?P<payperiod_id>\d+)/$', GeneratePayrollView.as_view(),
        name='new_payroll_list'),
    url('^payroll/reqauth/(?P<payroll_id>\d+)/$', PayrollRequestAuthorizationView.as_view(),
        name='payroll_request_authorize'),

    url('^payroll/(?P<payperiod_id>\d+)/auth/(?P<auth>\d+)/$',
        PayrollView.as_view(), name='payroll_list_auth'),
    url('^payroll/report/cycles_summary/$', PayrollCyclesSummaryReportView.as_view(),
        name='payroll_cycles_summary'),
    url('^payroll/report/payroll_summary/$', PayrollSummaryReportView.as_view(),
        name='payroll_summary_report'),
    url('^payroll/report/payroll_summary/csv/(?P<payroll_id>\d+)/(?P<dept_id>\d+)/$', payroll_summary_csv_report_view,
        name='payroll_summary_csv_report'),
    url('^payroll/report/payroll_summary/pdf/(?P<payroll_id>\d+)/(?P<dept_id>\d+)/$', PayrollSummaryPdfReportView.as_view(),
        name='payroll_summary_pdf_report'),
    url('^payroll/report/pdf/', PayrollReportPdfView.as_view(),
        name='payroll_pdf_report'),
    url('^payroll/report/excel/', payroll_csv_report_view,
        name='payroll_excel_report'),
    url('^payroll/sendslips/(?P<payperiod_id>\d+)/$', PayrollSendSlipsView.as_view(),
        name='payroll_send_slips'),

    url('^allowance/slip(?P<slip>\d+)/$', PayslipAllowanceView.as_view(),
        name='payslip_allowance'),
    url('^allowance/slip(?P<slip>\d+)/da(?P<da>\d+)/$',
        PayslipAllowanceView.as_view(), name='payslip_allowance_p'),
    url('^deduction/slip(?P<slip>\d+)/$', PayslipDeductionView.as_view(),
        name='deduction_list'),
    url('^deduction/slip(?P<slip>\d+)/dd/(?P<dd>\d+)/$', PayslipDeductionView.as_view(),
        name='payslip_deduction_del'),

    url('^payslip/days/slip(?P<pk>\d+)/$', PayslipTotalDaysWorkedView.as_view(), name='payslip_days'),
#    url('^payslip/odays/slip(?P<pk>\d+)/$', PayslipTotalOutreachDaysView.as_view(), name='outreach_days'),
    url('^payslip/detail/slip(?P<pk>\d+)/$', PayslipDetailView.as_view(),
        name='payslip_detail'),
    url('^payslip/pdfdetail/slip(?P<pk>\d+)/$', PayslipPdfDetailView.as_view(),
        name='payslip_pdf_detail'),
    url('^payslip/funds/slip(?P<slip>\d+)/$', PayslipFundsSourceView.as_view(), name='funds_list'),
    url('^payslip/funds/slip(?P<slip>\d+)/del(?P<del>\d+)/$', PayslipFundsSourceView.as_view(), name='funds_delete'),

#    url('^payslip/pdf/slip(?P<pk>\d+)/$', pdf_payslip, name='payslip_pdf'),
    url('^payslip/pdf/slip(?P<pk>\d+)/$', PdfPayslipList.as_view(),
        name='payslip_pdf'),

    url('^payslip/csv/(?P<pk>\d+)/$', payroll_csv_view, name='payslip_csv'),
    url('^payslip/sendslip/(?P<payslip_id>\d+)/$', PayslipSendView.as_view(),
        name='payslip_send'),

    url('^salaryscale/$', SalaryScaleListView.as_view(), name='salary_scale_list'),
    url('^salaryscale/new/$', SalaryScaleCreateView.as_view(),
        name='salary_scale_add'),
    url('^salaryscale/edit/(?P<pk>\d+)/$', SalaryScaleUpdateView.as_view(),
        name='salary_scale_edit'),
    url('^salaryscale/delete/(?P<pk>\d+)/$', SalaryScaleDeleteView.as_view(),
        name='salary_scale_delete'),

    url('^allowancetype/$', AllowanceTypeListView.as_view(),
        name='allowancetype_list'),
    url('^allowancetype/new/$', AllowanceTypeCreateView.as_view(),
        name='allowancetype_add'),
    url('^allowancetype/page(?P<page>[0-9]+)/$',
        AllowanceTypeListView.as_view(), name='allowancetype_list_p'),
    url('^allowancetype/edit/(?P<pk>\d+)/$', AllowanceTypeUpdateView.as_view(),
        name='allowancetype_edit'),
    url('^allowancetype/delete/$', AllowanceTypeDeleteView.as_view(),
        name='allowancetype_delete'),
    url('^allowancetype/delete/(?P<pk>\d+)/$', AllowanceTypeDeleteView.as_view()
        , name='allowancetype_delete_p'),

    url('^deductiontype/$', DeductionTypeListView.as_view(),
        name='deductiontype_list'),
    url('^deductiontype/new/$', DeductionTypeCreateView.as_view(),
        name='deductiontype_add'),
    url('^deductiontype/page(?P<page>[0-9]+)/$',
        DeductionTypeListView.as_view(), name='deductiontype_list_p'),
    url('^deductiontype/edit/(?P<pk>\d+)/$', DeductionTypeUpdateView.as_view(),
        name='deductiontype_edit'),
    url('^deductiontype/delete/$', DeductionTypeDeleteView.as_view(),
        name='deductiontype_delete'),
    url('^deductiontype/delete/(?P<pk>\d+)/$', DeductionTypeDeleteView.as_view()
        , name='deductiontype_delete_p'),

    url('^rec-adj/$', EmployeeRecurringAdjustmentListView.as_view(),
        name='emp_adj_list'),
    url('^rec-adj/page(?P<page>[0-9]+)/$', EmployeeRecurringAdjustmentListView.as_view(),
        name='emp_adj_list_p'),
    url('^rec-adj/(?P<show_adj_search_form>\w+)/(?P<search_data>\w+)/page(?P<page>\d+)/$',
        EmployeeRecurringAdjustmentListView.as_view(),
        name='emp_adj_list_s'),
    url('^rec-adj/add/(?P<type>\d+)/$', EmployeeRecurringAdjustmentCreateView.as_view(),
        name='emp_adj_add'),
    url('^rec-adj/update/(?P<pk>\d+)/$',
        EmployeeRecurringAdjustmentUpdateView.as_view(),
        name='emp_adj_update'),
    url('^rec-adj/delete/(?P<pk>\d+)/$',
        EmployeeRecurringAdjustmentDeleteView.as_view(),
        name='emp_adj_delete'),

    url('^position/$', PositionListView.as_view(), name='position_list'),
    url('^position/new/$', PositionCreateView.as_view(), name='position_add'),
    url('^position/page(?P<page>[0-9]+)/$', PositionListView.as_view(),
        name='position_list_p'),
    url('^position/edit/(?P<pk>\d+)/$', PositionUpdateView.as_view(), name='position_edit'),
    url('^position/delete/$', PositionDeleteView.as_view(), name='position_delete'),
    url('^position/delete/(?P<pk>\d+)/$', PositionDeleteView.as_view(), name='position_delete_p'),

    url('^branch/$', BranchListView.as_view(), name='branch_list'),
    url('^branch/new/$', BranchCreateView.as_view(), name='branch_add'),
    url('^branch/page(?P<page>[0-9]+)/$', BranchListView.as_view(),
        name='branch_list_p'),
    url('^branch/edit/(?P<pk>\d+)/$', BranchUpdateView.as_view(), name='branch_edit'),
    url('^branch/delete/$', BranchDeleteView.as_view(), name='branch_delete'),
    url('^branch/delete/(?P<pk>\d+)/$', BranchDeleteView.as_view(), name='branch_delete_p'),

    url('^nationality/$', NationalityListView.as_view(), name='nat_list'),
    url('^nationality/page(?P<page>[0-9]+)/$', NationalityListView.as_view(),
        name='nat_list_p'),
    url('^nationality/new/$', NationalityCreateView.as_view(), name='nat_add'),
    url('^nationality/edit/(?P<pk>\d+)/$', NationalityUpdateView.as_view(),
        name='nat_edit'),
    url('^nationality/delete/(?P<pk>\d+)/$', NationalityDeleteView.as_view(),
        name='nat_delete'),

    url('^employeetitle/$', EmployeeTitleListView.as_view(),
        name='employeetitle_list'),
    url('^employeetitle/new/$', EmployeeTitleCreateView.as_view(),
        name='employeetitle_add'),
    url('^employeetitle/page(?P<page>[0-9]+)/$',
        EmployeeTitleListView.as_view(), name='employeetitle_list_p'),
    url('^employeetitle/edit/(?P<pk>\d+)/$', EmployeeTitleUpdateView.as_view(),
        name='employeetitle_edit'),
    url('^employeetitle/delete/$', EmployeeTitleDeleteView.as_view(),
        name='employeetitle_delete_p'),
    url('^employeetitle/delete/(?P<pk>\d+)/$', EmployeeTitleDeleteView.as_view()
        , name='employeetitle_delete'),

    url('^report/paye/$', PayeReportView.as_view(), name='paye_report'),
    url('^report/paye/excel/(?P<pk>\d+)/$', paye_report_csv_view,
        name='paye_excel_report'),
    url('^report/paye/pdf/(?P<pk>\d+)/$', PayeReportPdfView.as_view(),
        name='paye_pdf_report'),

    url('^report/nssf/$', NssfReportView.as_view(), name='nssf_report'),
    url('^report/nssf/excel/(?P<pk>\d+)/$', nssf_report_csv_view,
        name='nssf_excel_report'),
    url('^report/nssf/pdf/(?P<pk>\d+)/$', NssfReportPdfView.as_view(),
        name='nssf_pdf_report'),
    url('^report/bank/$', BankReportView.as_view(), name='bank_report'),
    url('^report/bank/excel/(?P<pk>\d+)/$', bank_report_csv_view,
        name='bank_excel_report'),
#    url('^report/bank/excel/(?P<pk>\d+)/(?P<bank>\d+)/$', bank_report_csv_view),
    url('^report/bank/pdf/(?P<pk>\d+)/$', BankReportPdfView.as_view(),
        name='bank_pdf_report'),
    url('^report/salary/$', SalaryProgressionView.as_view(), name='salary_progression_report'),
    url('^salary/pdf/(?P<pk>\d+)/(?P<from>.+)/(?P<to>.+)/$', SalaryProgressionPdfReportView.as_view(),
        name='salary_progression_pdf'),
] + qualification_patterns + employee_patterns + administration_patterns
