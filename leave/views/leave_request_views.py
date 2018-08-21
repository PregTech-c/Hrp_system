__author__ = "Steven Kawuma <kawuma@gmail.com>"
__date__ = "Feb 15, 2017 9:31:46 AM"

from django.views.generic import View, ListView, CreateView
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.contrib import messages

from digg_paginator import DiggPaginator

from leave.models import LeaveRequest, LeaveType, LeaveApprover, LeaveApplicationReview
from leave.forms import LeaveRequestForm, LeaveApplicationReviewForm

from ..conf import settings

PGN = {'body': 10, 'padding': 1, 'tail': 5, 'padding': 2}

class LeaveRequestListView(ListView):

    template_name = 'leave_requests/leave_request_list.html'
    context_object_name = "leave_request_list"
    paginate_by = 5
    category = ''

    def get(self, request, *args, **kwargs):
        try:
            cancel_request = LeaveRequest.objects.get(
                pk=kwargs.get('cancel_pk'))
            count = cancel_request.messages.exclude(leave_status='C'
                ).update(leave_status='C')
            if count > 0:
                messages.success(self.request,
                    'Your leave request "{}" has been {} canceled.'.format(
                        cancel_request, count
                    ))
        except:
            pass
        return super(LeaveRequestListView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        query = self.request.user.profile.leave_requests.order_by('start_date')
        f = self.kwargs.get('cat')
        self.category = f
        cat = {}
        if f is not None:
            for r in query:
                index = r.get_status()
                if cat.get(index) is None:
                    cat[index] = []
                cat[index].append(r)
            if cat.get(f):
                query = query.filter(pk__in=[r.pk for r in cat[f]])
            else:
                query = query.filter(pk__in=[r.pk for r in []])
        return query

    def get_context_data(self, **kwargs):

        context = super(LeaveRequestListView, self).get_context_data(**kwargs)
        profile = self.request.user.profile
#        leave_type_list = LeaveType.methods.get_for_user(profile)
        leave_type_list = LeaveType.objects.user_types(user=self.request.user)
        type_list = []
        for t in leave_type_list:
            t.no_of_days_left = t.count_no_of_days_left(
                profile=self.request.user.profile)
            type_list.append(t)

        additional_context= {
            'leave_type_list': type_list, # leave_type_list,
            'now': timezone.now(),
            'category': self.category,
            'paginator': DiggPaginator(self.get_queryset(),
                self.paginate_by, body=PGN['body'], tail=PGN['tail'], padding=PGN['padding']
                ).page(self.kwargs.get('page', 1))
        }
        context.update(additional_context)
        return context

class LeaveRequestCreateView(CreateView):

    model = LeaveRequest
    form_class = LeaveRequestForm
    template_name = 'leave/leave_request_form.html'

    def get_initial(self):
        return {'profile': self.request.user.profile}

    def get_form_kwargs(self):
        kwargs = super(LeaveRequestCreateView, self).get_form_kwargs()
#        leave_type_list = LeaveType.methods.get_for_user(
#            self.request.user.profile)
        leave_type_list = LeaveType.objects.user_types(user=self.request.user)
        kwargs['leave_type_queryset'] = leave_type_list
        return kwargs

    def get_success_url(self):
        leave_request = self.object

        leave_request.notify_approvers()
        # Notify employee
        leave_request.notify_employee()
        # Notify notify_supervisor
        leave_request.notify_supervisor()
        messages.success(self.request,
            'You leave request "{}" has been posted.'.format(leave_request))
        return reverse('leave:leave_request_list')

class LeaveApplicationListView(ListView):
    model = LeaveApplicationReview
    context_object_name = 'leave_application_list'
    paginate_by = 5
    template_name = 'leave/leave_application_list.html'
    category = ''

    def get_queryset(self):
        try:
            query = LeaveApplicationReview.objects.all_applications(
                profile=self.request.user.profile)
        except:
            query = LeaveApplicationReview.objects.none()

        f = self.kwargs.get('cat')
        self.category = f
        if f is not None:
            query = query.filter(leave_status=f)
            self.category = f
        return query

    def get_context_data(self, **kwargs):
        context = super(LeaveApplicationListView, self).get_context_data(**kwargs)
        context.update({
            'category': self.category,
            'paginator': DiggPaginator(self.get_queryset(),
            self.paginate_by,
            body=PGN['body'], tail=PGN['tail'], padding=PGN['padding']
            ).page(self.kwargs.get('page', 1))
        })
        return context

class LeaveApplicationDetail(View):

    template_name = 'leave/leave_application_detail.html'

    def get(self, request, *args, **kwargs):

        application = LeaveApplicationReview.objects.get(pk=kwargs.get('pk'))
        initial = {
#            'request': application.request,
#            'reviewer': request.user,
            'reviewed_at': timezone.now(),
        }

        form = LeaveApplicationReviewForm(instance=application, initial=initial)

        return render(request, self.template_name, {
            'application': application,
            'form': form
        })

    def post(self, request, *args, **kwargs):

        application = LeaveApplicationReview.objects.get(pk=kwargs.get('pk'))
        form = LeaveApplicationReviewForm(request.POST, instance=application)

        if form.is_valid():
            instance = form.save()
            messages.success(request, "{} {}'s leave request.".format(
                instance.get_leave_status_display(),
                instance.get_leave_no_of_days(),
                instance.request.profile.get_fullname()
            ))

            return redirect('leave:leave_application_list')
        else:
            return render(request, self.template_name, {
                'application': form.instance.application,
                'form': form,
                'now': timezone.now(),
            })
