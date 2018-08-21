from django.views.generic import *
from payroll.models import *
from payroll.forms import SalaryScaleForm
from django.core.urlresolvers import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin

class SalaryScaleListView(ListView):
    model = SalaryScale
    template_name = 'administration/salaryscale_list.html'
    context_object_name = 'salary_scale_list'
    paginate_by = 10

class SalaryScaleCreateView(SuccessMessageMixin, CreateView):
    form_class = SalaryScaleForm
    template_name = 'administration/salary_scale_form.html'
    success_url = reverse_lazy('payroll:salary_scale_list')
    success_message = '%(code)s has been successfully created.'


class SalaryScaleUpdateView(SuccessMessageMixin, UpdateView):
    model = SalaryScale
    form_class = SalaryScaleForm
    template_name = 'administration/salary_scale_form.html'
    success_url = reverse_lazy('payroll:salary_scale_list')
    success_message = '%(code)s has been successfully edited.'

class SalaryScaleDeleteView(DeleteView):
    model = SalaryScale
    template_name = 'administration/salaryscale_confirm_delete.html'
    success_message = '%(code)s has been successfully deleted.'
    success_url = reverse_lazy('payroll:salary_scale_list')
