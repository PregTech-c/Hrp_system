from django.views.generic import *
from payroll.models import *  
from payroll.forms import UnitForm
from django.core.urlresolvers import reverse

class UnitListView(ListView):
    model = Branch
    context_object_name = 'branch_list'
    paginate_by = 10
    queryset = Branch.objects.filter().order_by('name')

    def get_context_data(self, **kwargs):
        context = super(UnitListView, self).get_context_data(**kwargs)
        try:
            if self.request.session['page_message']:
                context['page_message'] = '%s' % self.request.session['page_message']
                self.request.session['page_message'] = ''
        except:
            None
        return context

class UnitCreateView(CreateView):
    form_class = BranchForm

    template_name = 'branch_form.html'
    def get_success_url(self):
        return reverse('payroll:unit_list')

    def get_context_data(self, **kwargs):
        context = super(UnitCreateView, self).get_context_data(**kwargs)
        context['action_url'] = reverse('payroll:branch_add')
        return context

    def form_valid(self, form):
        self.request.session['page_message'] = \
            '%s has been successfully created.' % form.data['name']
        return super(UnitCreateView, self).form_valid(form)

class UnitUpdateView(UpdateView):
    model = Unit
    form_class = UnitForm
    template_name = 'branch_form.html'

    def get_success_url(self):
        return reverse('payroll:branch_list')

    def get_context_data(self, **kwargs):
        context = super(BranchUpdateView, self).get_context_data(**kwargs)
        context['action_url'] = reverse('payroll:branch_edit', kwargs={'pk': self.kwargs['pk']})
        return context

    def form_valid(self, form):
        self.request.session['page_message'] = '%s has been successfully modified.' % \
            str(self.get_object().name)
        return super(BranchUpdateView, self).form_valid(form)

class BranchDeleteView(DeleteView):
    model = Branch
    def get_success_url(self):
        return reverse('payroll:branch_list')

 
    def delete(self, request, *args, **kwargs):
        request.session['page_message'] = '%s has been successfully deleted' % \
            str(self.get_object().name)
        return super(BranchDeleteView, self).delete(request, *args, **kwargs)