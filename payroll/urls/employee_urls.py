__author__ = "Steven Kawuma <kawuma@gmail.com>"
__date__ = "Feb 8, 2017 3:32:37 PM"

from django.conf.urls import url
from payroll.views.employee_views import *

employee_patterns = [

    url('^user/$', EmployeeListView.as_view(), name='user_list'),
    url('^user/page(?P<page>[0-9]+)/$', EmployeeListView.as_view(),
        name='user_list_p'),
    url('^user/new/$', EmployeeCreateOrUpdateView.as_view(), name='user_add'),
    url('^user/search/$', EmployeeSearchView.as_view(), name='user_search'),
    url('^user/delete/(?P<pk>[0-9]+)/$', EmployeeDeleteView.as_view(),
        name='user_delete'),
    url('^user/update/(?P<pk>[0-9]+)/$', EmployeeCreateOrUpdateView.as_view(),
        name='user_edit'),
    url('^user/changepwd/$', UserChangePasswordView.as_view(),
        name='change_password'),
        
    url('^user/detail/(?P<pk>\d+)/$', EmployeeDetailView.as_view(),
        name='user_detail'),
    url('^user/sendpassword/(?P<pk>\d+)/$', EmployeeSendPasswordView.as_view(),
        name='user_send_password'),

    url('^user/report/$', EmployeeReportView.as_view(), name='user_report'),
#    url('^user/report/pdf/$', employee_pdf_view, name='user_pdf_report'),
    url('^user/report/pdf/$', EmployeePdfReportView.as_view(), name='user_pdf_report'),
    url('^user/report/excel/$', employee_csv_view, name='user_excel_report'),

    url('^profile/upload_photo/(?P<pk>\d+)/$', UploadEmployeePhotoView.as_view(), 
        name='emp_upload_photo'),
    url('^profile/upload_doc/(?P<pk>\d+)/$', UploadEmployeeDocumentView.as_view(), 
        name='emp_upload_doc'),
    url('^profile/remove_doc/(?P<pk>\d+)/(?P<doc_id>\d+)/$', RemoveEmployeeDocumentView.as_view(), 
        name='emp_remove_doc'),

]