__author__ = "Steven Kawuma <kawuma@gmail.com>"
__date__ = "Jan 24, 2017 5:24:43 AM"

from django.contrib import messages
from django.http import JsonResponse
from django.views.generic import *
from django.core.urlresolvers import reverse

from payroll.models.qualification_models import *
from payroll.forms.qualification_forms import *
from digg_paginator import DiggPaginator

PGN = {'body': 10, 'padding': 1, 'tail': 5, 'padding': 2}

class EducationLevelListView(ListView):
    model = EducationLevel
    context_object_name = 'educ_level_list'
    paginate_by = 10
    template_name = 'qualifications/educationlevel_list.html'

    def get_context_data(self, **kwargs):
        context = super(EducationLevelListView, self).get_context_data(**kwargs)
        context['paginator'] = DiggPaginator(self.get_queryset(), 
            self.paginate_by, 
            body=PGN['body'], tail=PGN['tail'], padding=PGN['padding']
            ).page(self.kwargs.get('page', 1))
        return context
    
class EducationLevelCreateView(CreateView):
    
    model = EducationLevel
    form_class = EducationLevelForm
    template_name = 'qualifications/educationlevel_form.html'
    
    def get_success_url(self):
        return reverse('payroll:educ_level_list')

    def form_valid(self, form):
        f = super(EducationLevelCreateView, self).form_valid(form)
        if self.request.POST.get('ajax'):
            return JsonResponse({
                'status': 0,
                'id': form.instance.id, 
                'qualification': str(form.instance)
            })
        else:
            messages.success(self.request, 
                '{} has been successfully created.'.format(self.object.level))
        return f
    
    def form_invalid(self, form):
        if self.request.POST.get('ajax'):
            return JsonResponse({
                'status': 1,
                'error': "{}".format(form.errors.as_text())
            })

class EducationLevelUpdateView(UpdateView):
    model = EducationLevel
    form_class = EducationLevelForm
    template_name = 'qualifications/educationlevel_form.html'

    def get_success_url(self):
        messages.success(self.request,
            '{} has been updated.'.format(self.object))
        return reverse('payroll:educ_level_list')

class EducationLevelDeleteView(DeleteView):
    model = EducationLevel
    template_name = 'qualifications/educationlevel_confirm_delete.html'

    def get_success_url(self):
        messages.success(self.request,
            '{} has been successfully deleted'.format(self.get_object()))
        return reverse('payroll:educ_level_list')

class SkillListView(ListView):
    model = Skill
    context_object_name = 'skill_list'
    paginate_by = 10
    template_name = 'qualifications/skill_list.html'

    def get_context_data(self, **kwargs):
        context = super(SkillListView, self).get_context_data(**kwargs)
        context['paginator'] = DiggPaginator(self.get_queryset(), 
            self.paginate_by, 
            body=PGN['body'], tail=PGN['tail'], padding=PGN['padding']
            ).page(self.kwargs.get('page', 1))
        return context

class SkillCreateView(CreateView):
    
    model = Skill
    form_class = SkillForm
    template_name = 'qualifications/skill_form.html'
    
    def get_success_url(self):
        return reverse('payroll:skill_list')
    
    def form_valid(self, form):
        f = super(SkillCreateView, self).form_valid(form)
        if self.request.POST.get('ajax'):
            return JsonResponse({
                'status': 0,
                'id': form.instance.id, 
                'name': str(form.instance.name)
            })
        else:
            messages.success(self.request, 
                '{} has been successfully created.'.format(self.object))
        return f
    
    def form_invalid(self, form):
        if self.request.POST.get('ajax'):
            return JsonResponse({
                'status': 1,
                'error': "{}".format(form.errors.as_text())
            })

class SkillUpdateView(UpdateView):
    model = Skill
    form_class = SkillForm
    template_name = 'qualifications/skill_form.html'

    def get_success_url(self):
        messages.success(self.request, 
            '{} has been updated.'.format(self.object))
        return reverse('payroll:skill_list')

class SkillDeleteView(DeleteView):
    model = Skill
    template_name = 'qualifications/skill_confirm_delete.html'

    def get_success_url(self):
        messages.success(self.request,
            '{} has been successfully deleted'.format(self.get_object()))
        return reverse('payroll:skill_list')

class CertificationListView(ListView):
    model = Certification
    context_object_name = 'certification_list'
    paginate_by = 10
    template_name = 'qualifications/certification_list.html'

    def get_context_data(self, **kwargs):
        context = super(CertificationListView, self).get_context_data(**kwargs)
        context['paginator'] = DiggPaginator(self.get_queryset(), 
            self.paginate_by, 
            body=PGN['body'], tail=PGN['tail'], padding=PGN['padding']
            ).page(self.kwargs.get('page', 1))
        return context

class CertificationCreateView(CreateView):
    
    model = Certification
    form_class = CertificationForm
    template_name = 'qualifications/certification_form.html'
    
    def get_success_url(self):
        return reverse('payroll:cert_list')

    def form_valid(self, form):
        f = super(CertificationCreateView, self).form_valid(form)
        if self.request.POST.get('ajax'):
            return JsonResponse({
                'status': 0,
                'id': form.instance.id, 
                'name': str(form.instance)
            })
        else:
            messages.success(self.request, 
                '{} has been successfully created.'.format(self.object))
        return f
    
    def form_invalid(self, form):
        if self.request.POST.get('ajax'):
            return JsonResponse({
                'status': 1,
                'error': "{}".format(form.errors.as_text())
            })

class CertificationUpdateView(UpdateView):
    model = Certification
    form_class = CertificationForm
    template_name = 'qualifications/certification_form.html'

    def get_success_url(self):
        messages.success(self.request, 
            '{} has been updated.'.format(self.object))
        return reverse('payroll:cert_list')

class CertificationDeleteView(DeleteView):
    model = Certification
    template_name = 'qualifications/certification_confirm_delete.html'

    def get_success_url(self):
        messages.success(self.request,
            '{} has been successfully deleted'.format(self.get_object()))
        return reverse('payroll:cert_list')

class MembershipListView(ListView):
    model = Membership
    context_object_name = 'membership_list'
    paginate_by = 10
    template_name = 'qualifications/membership_list.html'

    def get_context_data(self, **kwargs):
        context = super(MembershipListView, self).get_context_data(**kwargs)
        context['paginator'] = DiggPaginator(self.get_queryset(), 
            self.paginate_by, 
            body=PGN['body'], tail=PGN['tail'], padding=PGN['padding']
            ).page(self.kwargs.get('page', 1))
        return context

class MembershipCreateView(CreateView):
    
    model = Membership
    form_class = MembershipForm
    template_name = 'qualifications/membership_form.html'
    
    def get_success_url(self):
        return reverse('payroll:membership_list')

    def form_valid(self, form):
        f = super(MembershipCreateView, self).form_valid(form)
        if self.request.POST.get('ajax'):
            return JsonResponse({
                'status': 0,
                'id': form.instance.id, 
                'name': str(form.instance.name)
            })
        else:
            messages.success(self.request, 
                '{} has been successfully created.'.format(self.object))
        return f
    
    def form_invalid(self, form):
        if self.request.POST.get('ajax'):
            return JsonResponse({
                'status': 1,
                'error': "{}".format(form.errors.as_text())
            })

class MembershipUpdateView(UpdateView):
    model = Membership
    form_class = MembershipForm
    template_name = 'qualifications/membership_form.html'

    def get_success_url(self):
        messages.success(self.request, 
            '{} has been updated.'.format(self.object))
        return reverse('payroll:membership_list')

class MembershipDeleteView(DeleteView):
    model = Membership
    template_name = 'qualifications/membership_confirm_delete.html'

    def get_success_url(self):
        messages.success(self.request,
            '{} has been successfully deleted'.format(self.get_object()))
        return reverse('payroll:membership_list')

class LanguageListView(ListView):
    model = Language
    context_object_name = 'language_list'
    paginate_by = 10
    template_name = 'qualifications/language_list.html'

    def get_context_data(self, **kwargs):
        context = super(LanguageListView, self).get_context_data(**kwargs)
        context['paginator'] = DiggPaginator(self.get_queryset(), 
            self.paginate_by, 
            body=PGN['body'], tail=PGN['tail'], padding=PGN['padding']
            ).page(self.kwargs.get('page', 1))
        return context

class LanguageCreateView(CreateView):
    
    model = Language
    form_class = LanguageForm
    template_name = 'qualifications/language_form.html'
    
    def get_success_url(self):
        messages.success(self.request, 
            '{} has been successfully created.'.format(self.object))
        return reverse('payroll:lang_list')

class LanguageUpdateView(UpdateView):
    model = Language
    form_class = LanguageForm
    template_name = 'qualifications/language_form.html'

    def get_success_url(self):
        messages.success(self.request, 
            '{} has been updated.'.format(self.object))
        return reverse('payroll:lang_list')

class LanguageDeleteView(DeleteView):
    model = Language
    template_name = 'qualifications/language_confirm_delete.html'

    def get_success_url(self):
        messages.success(self.request,
            '{} has been successfully deleted'.format(self.get_object()))
        return reverse('payroll:lang_list')
