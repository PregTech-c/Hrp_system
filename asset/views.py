from django.views.generic import (ListView, CreateView, UpdateView,
    DeleteView)

from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin

from django.shortcuts import reverse
from django.core.urlresolvers import reverse_lazy
from django.utils import timezone
from django.db.models import Q

from .models import Asset, AssetIssuance
from .forms import AssetIssuanceForm, AssetReturnForm, AssetIssuanceSearchForm
from payroll.forms.hrp_widgets import *

from digg_paginator import DiggPaginator

class AssetListView(ListView):
    
    template_name = 'asset/asset_list.html'
    context_object_name = "asset_list"
    paginate_by = 5
    category = ''
    
    def get_queryset(self):
        return Asset.objects.all()

class AssetCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):

    model = Asset
    fields = ['category', 'id_type', 'id_number', 'date_of_manufacture',
        'description']
    template_name = 'asset/asset_form.html'
    success_message = "%(category)s with %(id_type)s %(id_number)s " \
        "has been registered."
    success_url = reverse_lazy('asset:asset_list')
    permission_required = 'asset.add_asset'
    
    def get_form(self):
        form = super(AssetCreateView, self).get_form()
        form.fields['category'].empty_label = None
        form.fields['id_type'].empty_label = None
        form.fields['date_of_manufacture'].widget = JQueryUIDatepickerWidget()
        return form

class AssetUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):

    model = Asset
    fields = ['category', 'id_type', 'id_number', 'date_of_manufacture',
        'description']
    template_name = 'asset/asset_form.html'
    success_message = "%(category)s with %(id_type)s %(id_number)s has been updated."
    success_url = reverse_lazy('asset:asset_list')
    permission_required = 'asset.change_asset'

    def get_form(self):
        form = super(AssetUpdateView, self).get_form()
        form.fields['category'].empty_label = None
        form.fields['id_type'].empty_label = None
        form.fields['date_of_manufacture'].widget = JQueryUIDatepickerWidget()
        return form

class AssetDeleteView(PermissionRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Asset
    template_name = 'asset/asset_confirm_delete.html'
    success_url = reverse_lazy('asset:asset_list')
    success_message = '"%(name)s" has been successfully deleted.'
    failure_message = '"%(name)s" cannot be deleted because there ' \
        'are records that refer to it.'
    permission_required = 'asset.delete_asset'

    def get_success_url(self):
        messages.success(self.request,
            '{} has been deleted.'.format(self.object))
        return reverse('asset:asset_list')

class AssetIssuanceListView(ListView):
    model = Asset
    template_name = 'asset/assetissuance_list.html'
#    context_object_name = "issuance_list"
    paginate_by = 10
    paginator_class = DiggPaginator
    
    def get_queryset(self):
        q = Asset.objects.all()
        if self.kwargs.get('search_data') == 'off':
            if self.request.session.get('search_criteria'):
                del self.request.session['search_criteria']
        
        search_criteria = self.request.session.get('search_criteria')
        f = Q()

        if search_criteria:
            if search_criteria.get('category'):
                f = Q(category=search_criteria['category'])
            if search_criteria.get('employee'):
                f = Q(f&Q(issues__returned_date__isnull=True, 
                        issues__employee=search_criteria['employee']))
            
            issue_status = search_criteria.get('issue_status')
            if int(issue_status):
                issued = True if search_criteria.get('issue_status') == '1' else False
                f = Q(f&Q(issues__returned_date__isnull=issued))
                
        return q.filter(f).distinct()
    
    def get_context_data(self, **kwargs):
        search_form = self.kwargs.get('show_asset_search_form', 'off')
        
        search_data = 'off'
        if self.request.session.get('search_criteria'):
            form = AssetIssuanceSearchForm(
                self.request.session.get('search_criteria'))
            search_data = 'on'
            search_form = 'on'
        elif self.request.method == 'POST':
            form = AssetIssuanceSearchForm(self.request.POST)
            search_data = 'on'
            search_form = 'on'
        else:
            form = AssetIssuanceSearchForm()

        context = super(AssetIssuanceListView, self).get_context_data(**kwargs)
        context.update({
            'search_form': form,
            'show_search_form': search_form,
            'pg_url': "/asset/allocation/{}/{}/".format(
                search_form,
                search_data),
        })
        return context
    
    def post(self, request, *args, **kwargs):
        search_form = AssetIssuanceSearchForm(request.POST)
        if search_form.is_valid():
            request.session['search_criteria'] = search_form.cleaned_data
        else:
            ctx = self.get_context_data()
            ctx['form'] = form
            ctx['search_data'] = 'on'
            return render(request, self.template_name, ctx) 
        return super(AssetIssuanceListView, self).get(request, *args, **kwargs)
    
class AssetIssuanceFormView(PermissionRequiredMixin, SuccessMessageMixin, 
        CreateView):
    form_class = AssetIssuanceForm
    permission_required = 'asset.change_assetissuance'
    model = AssetIssuance
    success_url = reverse_lazy('asset:asset_allocation_list')
    success_message = "You have assigned %(employee)s %(asset)s."
    
    def get_initial(self):
        return {'asset': self.kwargs.get('asset_id')}
    
    def get_context_data(self, **kwargs):
        context = super(AssetIssuanceFormView, self).get_context_data(**kwargs)
        context['asset'] = Asset.objects.get(pk=self.kwargs.get('asset_id'))
        return context

class AssetReturnFormView(PermissionRequiredMixin, SuccessMessageMixin, 
        UpdateView):
    form_class = AssetReturnForm
    permission_required = 'asset.change_assetissuance'
    model = AssetIssuance
    success_url = reverse_lazy('asset:asset_allocation_list')
    success_message = "Return of %(asset)s by %(employee)s has been registered."
    
    def get_initial(self):
        initial = super(AssetReturnFormView, self).get_initial()
        initial['returned_date'] = timezone.now()
        return initial
    
    def get_context_data(self, **kwargs):
        context = super(AssetReturnFormView, self).get_context_data(**kwargs)
        context['asset'] = self.object.asset
        return context