__author__ = "Steven Kawuma <kawuma@gmail.com>"
__date__ = "Feb 14, 2017 3:06:12 PM"

from django.conf.urls import url
from leave.views import *

urlpatterns = [

    url('^holiday/new/$', HolidayCreateView.as_view(), name='holiday_create'),
    url('^holiday/$', HolidayListView.as_view(), name='holiday_list'),
    url('^holiday/page(?P<page>\d+)/$', HolidayListView.as_view(),
        name='holiday_list_p'),    
    url('^holiday/edit/(?P<pk>\d+)/$', HolidayUpdateView.as_view(), 
        name='holiday_edit'),
    url('^holiday/delete/(?P<pk>\d+)/$', HolidayDeleteView.as_view(), 
        name='holiday_delete'),
        
    url('^lperiod/new/$', LeavePeriodCreateView.as_view(), 
        name='leave_period_create'),
    url('^lperiod/$', LeavePeriodListView.as_view(), name='leave_period_list'),
    url('^lperiod/page(?P<page>\d+)/$', LeavePeriodListView.as_view(),
        name='leave_period_list_p'),    
    url('^lperiod/edit/(?P<pk>\d+)/$', LeavePeriodUpdateView.as_view(), 
        name='leave_period_edit'),
    url('^lperiod/delete/(?P<pk>\d+)/$', LeavePeriodDeleteView.as_view(), 
        name='leave_period_delete'),

    url('^ltype/new/$', LeaveTypeCreateView.as_view(), 
        name='leave_type_create'),
    url('^ltype/$', LeaveTypeListView.as_view(), name='leave_type_list'),
    url('^ltype/page(?P<page>\d+)/$', LeaveTypeListView.as_view(),
        name='leave_type_list_p'),    
    url('^ltype/edit/(?P<pk>\d+)/$', LeaveTypeUpdateView.as_view(), 
        name='leave_type_edit'),
    url('^ltype/delete/(?P<pk>\d+)/$', LeaveTypeDeleteView.as_view(), 
        name='leave_type_delete'),

    url('^lapprover/$', LeaveApproverView.as_view(), name='leave_approvers'),
    url('^lapprover/(?P<rem_pk>\d+)/rem/$', LeaveApproverView.as_view(), 
        name='leave_approver_remove'),

    url('^lrequest/$', LeaveRequestListView.as_view(), 
        name='leave_request_list'),
    url('^lrequest/(?P<cat>[P|A|E|C|D]+)/$', LeaveRequestListView.as_view(), 
        name='leave_request_list_f'),
    url('^lrequest/(?P<cat>[P|A|E|C|D]+)/page(?P<page>\d+)/$', LeaveRequestListView.as_view(), 
        name='leave_request_list_f_p'),
    url('^lrequest/page(?P<page>\d+)/$', LeaveRequestListView.as_view(),
        name='leave_request_list_p'),    
    url('^lrequest/(?P<cancel_pk>\d+)/cancel/$', LeaveRequestListView.as_view(), 
        name='leave_request_cancel'),
    url('^lrequest/new/$', LeaveRequestCreateView.as_view(), 
        name='leave_request_create'),

    url('^larequest/$', LeaveApplicationListView.as_view(), 
        name='leave_application_list'),
    url('^larequest/(?P<cat>[P|A|E|C|D]+)/$', LeaveApplicationListView.as_view(), 
        name='leave_application_list_f'),
    url('^larequest/(?P<cat>[P|A|E|C|D]+)/page(?P<page>\d+)/$', LeaveApplicationListView.as_view(), 
        name='leave_application_list_f_p'),
    url('^larequest/page(?P<page>\d+)/$', LeaveApplicationListView.as_view(),
        name='leave_application_list_p'),    
    url('^lapplication/(?P<pk>\d+)/$', LeaveApplicationDetail.as_view(),
        name='leave_application_detail'),   

    url('^lonleave/(?P<search>\w+)/(?P<show_form>\w+)/$', OnLeaveReportView.as_view(), 
        name='leave_report_on_leave'),
#    url('^lonleave/(?P<search>)/$', OnLeaveReportView.as_view(), 
#        name='leave_report_on_leave'),
    url('^lonleave/(?P<cat>[P|A|E|C|D]+)/page(?P<page>\d+)/$', OnLeaveReportView.as_view(), 
        name='leave_report_on_leave_p'),
    url('^lonleave/pdf/$', OnLeavePdfReportView.as_view(), 
        name='leave_report_on_leave_pdf'),
    url('^leave/detail/(?P<pk>\d+)/$', LeaveRequestDetailView.as_view(), 
        name='leave_request_detail'),
    url('^leave/detail/pdf/(?P<pk>\d+)/$', LeaveRequestPdfDetailView.as_view(), 
        name='leave_request_detail_pdf'),

]