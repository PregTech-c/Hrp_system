__author__ = "Steven Kawuma <kawuma@gmail.com>"
__date__ = "May 11, 2017 2:19:42 PM"
from django.conf.urls import url
from payroll.views.serviceline_views import *

administration_patterns = [

    url('^sltype/$', ServiceLineTypeListView.as_view(), name='sl_type_list'),
    url('^sltype/add/$', ServiceLineTypeCreateView.as_view(), name='sl_type_add'),
    url('^sltype/edit/(?P<pk>\d+)/$', ServiceLineTypeUpdateView.as_view(), 
        name='sl_type_edit'),
    url('^sltype/delete/$', ServiceLineTypeDeleteView.as_view(), 
        name='sl_type_delete_p'),
    url('^sltype/delete/(?P<pk>\d+)/$', ServiceLineTypeDeleteView.as_view(), 
        name='sl_type_delete'),

    url('^sl/$', ServiceLineListView.as_view(), name='sl_list'),
    url('^sl/new/$', ServiceLineCreateView.as_view(), name='sl_add'),
    url('^sl/edit/(?P<pk>\d+)/$', ServiceLineUpdateView.as_view(), 
        name='sl_edit'),
    url('^sl/delete/$', ServiceLineDeleteView.as_view(), name='sl_delete_p'),
    url('^sl/delete/(?P<pk>\d+)/$', ServiceLineDeleteView.as_view(), 
        name='sl_delete'),

]