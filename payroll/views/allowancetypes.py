from django.views.generic import *
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin

from payroll.models import *
from payroll.forms import AllowanceTypeForm

class AllowanceTypeListView(ListView):
    model = AllowanceType
    template_name = 'administration/allowancetype_list.html'
    context_object_name = 'allowancetype_list'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(AllowanceTypeListView, self).get_context_data(**kwargs)
        try:
            if self.request.session['page_message']:
                context['page_message'] = '%s' % self.request.session['page_message']
                self.request.session['page_message'] = ''
        except:
            None
        return context

class AllowanceTypeCreateView(SuccessMessageMixin, CreateView):
    form_class = AllowanceTypeForm
    success_url = reverse_lazy('payroll:allowancetype_list')
    template_name = 'administration/allowancetype_form.html'
    success_message = 'Type "%(name)s" has been successfully created.'

class AllowanceTypeUpdateView(SuccessMessageMixin, UpdateView):
    model = AllowanceType
    form_class = AllowanceTypeForm
    template_name = 'administration/allowancetype_form.html'
    success_url = reverse_lazy('payroll:allowancetype_list')
    success_message = 'Type "%(name)s" has been successfully updated.'

class AllowanceTypeDeleteView(DeleteView):
    model = AllowanceType
    template_name = 'administration/allowancetype_confirm_delete.html'
    success_url = reverse_lazy('payroll:allowancetype_list')
    success_message = 'Type "%(name)s" has been successfully deleted.'
    failure_message = '"%(name)s" cannot be deleted because it reflects in previous records.'
    
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        try:
            view = super(AllowanceTypeDeleteView, self).delete(request, *args, **kwargs)
        except IntegrityError as e:
            messages.error(request, self.failure_message % obj.__dict__)
            return reverse('payroll:allowancetype_list')
        else:
            messages.success(request, self.success_message % obj.__dict__)
            return view
