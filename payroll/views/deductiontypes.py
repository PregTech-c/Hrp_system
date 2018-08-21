from django.views.generic import *
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages 

from payroll.models import *
from payroll.forms import DeductionTypeForm

class DeductionTypeListView(ListView):
    model = DeductionType
    template_name = 'administration/deductiontype_list.html'
    context_object_name = 'deductiontype_list'
    paginate_by = 10

class DeductionTypeCreateView(SuccessMessageMixin, CreateView):
    form_class = DeductionTypeForm
    success_url = reverse_lazy('payroll:deductiontype_list')
    template_name = 'administration/deductiontype_form.html'
    success_message = '%(name)s has been successfully created.'
    
class DeductionTypeUpdateView(SuccessMessageMixin, UpdateView):
    model = DeductionType
    form_class = DeductionTypeForm
    template_name = 'administration/deductiontype_form.html'
    success_url = reverse_lazy('payroll:deductiontype_list')
    success_message = '%(name)s has been successfully updated.'
    
class DeductionTypeDeleteView(DeleteView):
    model = DeductionType
    template_name = 'administration/deductiontype_confirm_delete.html'
    success_url = reverse_lazy('payroll:deductiontype_list')
    success_message = '%(name)s has been successfully deleted'
    failure_message = '"%(name)s" cannot be deleted because it reflects in previous records.'

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        try:
            view = super(DeductionTypeDeleteView, self).delete(request, *args, 
                **kwargs)
        except IntegrityError as e:
            messages.error(request, self.failure_message % obj.__dict__)
            return reverse('payroll:deductiontype_list')
        else:
            messages.success(request, self.success_message % obj.__dict__)
            return view
