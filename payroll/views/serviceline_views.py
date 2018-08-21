from django.views.generic import *
from django.core.urlresolvers import reverse

from payroll.models import *
from payroll.forms import ServiceLineForm, ServiceLineTypeForm

class ServiceLineListView(ListView):
    model = ServiceLine
    template_name = 'administration/serviceline_list.html'
    context_object_name = 'serviceline_list'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(ServiceLineListView, self).get_context_data(**kwargs)
        try:
            if self.request.session['page_message']:
                context['page_message'] = '%s' % self.request.session['page_message']
                self.request.session['page_message'] = ''
        except:
            None
        return context

class ServiceLineCreateView(CreateView):
    form_class = ServiceLineForm

    template_name = 'administration/serviceline_form.html'

    def get_success_url(self):
        return reverse('payroll:sl_list')

    def get_context_data(self, **kwargs):
        context = super(ServiceLineCreateView, self).get_context_data(**kwargs)
        context['action'] = 'Add'
        return context

    def form_valid(self, form):
        self.request.session['page_message'] = \
            '%s has been successfully created.' % form.data['name']
        return super(ServiceLineCreateView, self).form_valid(form)

class ServiceLineUpdateView(UpdateView):
    model = ServiceLine
    form_class = ServiceLineForm
    template_name = 'administration/serviceline_form.html'

    def get_success_url(self):
        return reverse('payroll:sl_list')

    def get_context_data(self, **kwargs):
        context = super(ServiceLineUpdateView, self).get_context_data(**kwargs)
        context['action'] = 'Edit'
        return context

    def form_valid(self, form):
        self.request.session['page_message'] = '%s has been successfully modified.' % \
            str(self.get_object().name)
        return super(ServiceLineUpdateView, self).form_valid(form)

class ServiceLineDeleteView(DeleteView):
    model = ServiceLine
    template_name = 'administration/serviceline_confirm_delete.html'

    def get_success_url(self):
        return reverse('payroll:sl_list')
    def delete(self, request, *args, **kwargs):
        request.session['page_message'] = '%s has been successfully deleted' % \
            str(self.get_object().name)
        return super(ServiceLineDeleteView, self).delete(request, *args, **kwargs)

class ServiceLineTypeCreateView(CreateView):
    form_class = ServiceLineTypeForm
    template_name = 'administration/serviceline_type_form.html'

    def get_success_url(self):
        return reverse('payroll:sl_type_list')

    def get_context_data(self, **kwargs):
        context = super(ServiceLineTypeCreateView, self).get_context_data(**kwargs)
        context['action'] = 'Add'
        return context

    def form_valid(self, form):
        self.request.session['page_message'] = \
            '"%s" has been successfully created.' % form.data['name']
        return super(ServiceLineTypeCreateView, self).form_valid(form)

class ServiceLineTypeListView(ListView):
    model = ServiceLineType
    template_name = 'administration/serviceline_type_list.html'
    context_object_name = 'serviceline_type_list'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(ServiceLineTypeListView, self).get_context_data(**kwargs)
        try:
            if self.request.session['page_message']:
                context['page_message'] = '%s' % self.request.session['page_message']
                self.request.session['page_message'] = ''
        except:
            None
        return context

class ServiceLineTypeUpdateView(UpdateView):
    model = ServiceLineType
    form_class = ServiceLineTypeForm
    template_name = 'administration/serviceline_type_form.html'

    def get_success_url(self):
        return reverse('payroll:sl_type_list')

    def get_context_data(self, **kwargs):
        context = super(ServiceLineTypeUpdateView, self).get_context_data(**kwargs)
        context['action'] = 'Edit'
        return context

    def form_valid(self, form):
        self.request.session['page_message'] = '"%s" has been successfully modified.' % \
            str(self.get_object().name)
        return super(ServiceLineTypeUpdateView, self).form_valid(form)

class ServiceLineTypeDeleteView(DeleteView):
    model = ServiceLineType
    template_name = 'administration/serviceline_type_confirm_delete.html'

    def get_success_url(self):
        return reverse('payroll:sl_type_list')
    def delete(self, request, *args, **kwargs):
        request.session['page_message'] = '%s has been successfully deleted' % \
            str(self.get_object().name)
        return super(ServiceLineTypeDeleteView, self).delete(request, *args, **kwargs)

