from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt

from recruitment.views import (
    VacancyCreateView, 
    VacancyListView, 
    VacancyUpdateView, 
    VacancyDetailView, 
    VacancyDeleteView,
    JobApplicationCreateView,
    ExternalJobApplicationCreateView,
    JobApplicationListView, 
    JobApplicationDetailView,
    EvaluationStageView,
    EvaluationStageDeleteView
)

urlpatterns = [

    url('^vac/page(?P<page>\d+)/$', VacancyListView.as_view(), 
        name='vacancy_list'),
    url('^vac/(?P<pk>\d+)/$', VacancyDetailView.as_view(), 
        name='vacancy_detail'),
    url('^vac/new/$', VacancyCreateView.as_view(), name='vacancy_add'),
    url('^vac/edit/(?P<pk>\d+)$', VacancyUpdateView.as_view(), 
        name='vacancy_edit'),
    url('^vac/del/(?P<pk>\d+)$', VacancyDeleteView.as_view(), 
        name='vacancy_delete'),

    url('^eval/(?P<vac_id>\d+)/page(?P<page>\d+)/$', EvaluationStageView.as_view(), 
        name='eval_list'),
    url('^eval/del/(?P<pk>\d+)$', EvaluationStageDeleteView.as_view(), 
        name='eval_delete'),

#    url('^app/page(?P<page>\d+)/$', JobApplicationListView.as_view(), 
#        name='application_list'),
    url('^app/(?P<vac_id>\d+)/page(?P<page>\d+)/$', JobApplicationListView.as_view(), 
        name='application_list'),
    url('^app/(?P<vac_id>\d+)/page(?P<page>\d+)/(?P<search>\w+)/(?P<show_form>\w+)$', JobApplicationListView.as_view(), 
        name='application_list_r'),
    url('^app/new/(?P<vac_id>\d+)/$', JobApplicationCreateView.as_view(), 
        name='application_add'),
    url('^app/new/ext/(?P<vac_id>\d+)/$', csrf_exempt(ExternalJobApplicationCreateView.as_view()), 
        name='application_add_ext'),
    url('^app/detail/(?P<pk>\d+)/$', JobApplicationDetailView.as_view(), 
        name='application_detail'),
        
]