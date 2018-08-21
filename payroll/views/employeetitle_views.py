from django.views.generic import *
from django.core.urlresolvers import reverse

from payroll.models import *
from payroll.forms import EmployeeTitleForm

class EmployeeTitleListView(ListView):
    model = EmployeeTitle
    template_name = 'administration/employeetitle_list.html'
    context_object_name = 'title_list'
    paginate_by = 10
    queryset = EmployeeTitle.objects.filter().order_by('name')

    def get_context_data(self, **kwargs):
        context = super(EmployeeTitleListView, self).get_context_data(**kwargs)
        try:
            if self.request.session['page_message']:
                context['page_message'] = '%s' % self.request.session['page_message']
                self.request.session['page_message'] = ''
        except:
            None
        return context

class EmployeeTitleCreateView(CreateView):
    form_class = EmployeeTitleForm

    template_name = 'administration/employeetitle_form.html'

    def get_success_url(self):
        return reverse('payroll:employeetitle_list')

    def get_context_data(self, **kwargs):
        context = super(EmployeeTitleCreateView, self).get_context_data(**kwargs)
        context['action_url'] = reverse('payroll:employeetitle_add')
        return context

    def form_valid(self, form):
        self.request.session['page_message'] = \
            '%s has been successfully created.' % form.data['name']
        return super(EmployeeTitleCreateView, self).form_valid(form)

class EmployeeTitleUpdateView(UpdateView):
    model = EmployeeTitle
    form_class = EmployeeTitleForm
    template_name = 'administration/employeetitle_form.html'

    def get_success_url(self):
        return reverse('payroll:employeetitle_list')

    def get_context_data(self, **kwargs):
        context = super(EmployeeTitleUpdateView, self).get_context_data(**kwargs)
        context['action_url'] = reverse('payroll:employeetitle_edit', kwargs={'pk': self.kwargs['pk']})
        return context

    def form_valid(self, form):
        self.request.session['page_message'] = '%s has been successfully modified.' % \
            str(self.get_object().name)
        return super(EmployeeTitleUpdateView, self).form_valid(form)

class EmployeeTitleDeleteView(DeleteView):
    model = EmployeeTitle
    template_name = 'administration/employeetitle_confirm_delete.html'

    def get_success_url(self):
        return reverse('payroll:employeetitle_list')

    def delete(self, request, *args, **kwargs):
        request.session['page_message'] = '%s has been successfully deleted' % \
            str(self.get_object().name)
        return super(EmployeeTitleDeleteView, self).delete(request, *args, **kwargs)