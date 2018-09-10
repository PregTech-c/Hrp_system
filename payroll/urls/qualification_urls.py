__author__ = "Steven Kawuma <kawuma@gmail.com>"
__date__ = "Jan 24, 2017 5:44:35 AM"
from django.conf.urls import url
from payroll.views.qualification_views import *

qualification_patterns = [

    url('^educ/$', EducationLevelListView.as_view(), name='educ_level_list'),
    url('^educ/page(?P<page>[0-9]+)/$', EducationLevelListView.as_view(),
        name='educ_level_list_p'),    
    url('^educ/new/$', EducationLevelCreateView.as_view(), name='educ_add'),
    url('^educ/edit/(?P<pk>\d+)/$', EducationLevelUpdateView.as_view(), 
        name='educ_level_edit'),
    url('^educ/delete/(?P<pk>\d+)/$', EducationLevelDeleteView.as_view(), 
        name='educ_level_delete'),

    url('^skill/$', SkillListView.as_view(), name='skill_list'),
    url('^skill/page(?P<page>[0-9]+)/$', SkillListView.as_view(),
        name='skill_list_p'),    
    url('^skill/new/$', SkillCreateView.as_view(), name='skill_add'),
    url('^skill/edit/(?P<pk>\d+)/$', SkillUpdateView.as_view(), 
        name='skill_edit'),
    url('^skill/delete/(?P<pk>\d+)/$', SkillDeleteView.as_view(), 
        name='skill_delete'),

    url('^cert/$', CertificationListView.as_view(), name='cert_list'),
    url('^cert/page(?P<page>[0-9]+)/$', CertificationListView.as_view(),
        name='skill_list_p'),    
    url('^cert/new/$', CertificationCreateView.as_view(), name='cert_add'),
    url('^cert/edit/(?P<pk>\d+)/$', CertificationUpdateView.as_view(), 
        name='cert_edit'),
    url('^cert/delete/(?P<pk>\d+)/$', CertificationDeleteView.as_view(), 
        name='cert_delete'),

    url('^membership/$', MembershipListView.as_view(), name='membership_list'),
    url('^membership/page(?P<page>[0-9]+)/$', MembershipListView.as_view(),
        name='membership_list_p'),    
    url('^membership/new/$', MembershipCreateView.as_view(), 
        name='membership_add'),
    url('^membership/edit/(?P<pk>\d+)/$', MembershipUpdateView.as_view(), 
        name='membership_edit'),
    url('^membership/delete/(?P<pk>\d+)/$', MembershipDeleteView.as_view(), 
        name='membership_delete'),

    url('^language/$', LanguageListView.as_view(), name='lang_list'),
    url('^language/page(?P<page>[0-9]+)/$', MembershipListView.as_view(),
        name='lang_list_p'),    
    url('^language/new/$', LanguageCreateView.as_view(), 
        name='lang_add'),
    url('^language/edit/(?P<pk>\d+)/$', LanguageUpdateView.as_view(), 
        name='lang_edit'),
    url('^language/delete/(?P<pk>\d+)/$', LanguageDeleteView.as_view(), 
        name='lang_delete'),


]