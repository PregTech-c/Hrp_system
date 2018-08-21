from django.conf.urls import url
from .views import *

urlpatterns = [

    url('^$', AssetListView.as_view(), name='asset_list'),
    url('^page(?P<page>\d+)/$', AssetListView.as_view(),
        name='asset_list_p'),    
    url('^new/$', AssetCreateView.as_view(), 
        name='asset_create'),
    url('^asset/edit/(?P<pk>\d+)/$', AssetUpdateView.as_view(), 
        name='asset_edit'),
    url('^asset/delete/(?P<pk>\d+)/$', AssetDeleteView.as_view(), 
        name='asset_delete'),

    url('^allocation/$', AssetIssuanceListView.as_view(), 
        name='asset_allocation_list'),
    url('^allocation/page(?P<page>\d+)/$', AssetIssuanceListView.as_view(),
        name='asset_allocation_list_p'),    
    url('^allocation/(?P<show_asset_search_form>\w+)/(?P<search_data>\w+)/page(?P<page>\d+)/$', 
        AssetIssuanceListView.as_view(),
        name='asset_allocation_list_s'),    
    url('^allocation/new/(?P<asset_id>\d+)/$', AssetIssuanceFormView.as_view(), 
        name='asset_allocation_add'),
    url('^allocation/update/(?P<pk>\d+)/$', AssetReturnFormView.as_view(), 
        name='asset_return'),
        
]