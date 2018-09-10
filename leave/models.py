from __future__ import unicode_literals

from django.contrib.auth.models import User, Permission
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.shortcuts import reverse

#from notify.signals import notify
import notify
from django_permanent.models import PermanentModel
from django_permanent.query import PermanentQuerySet, NonDeletedQuerySet
from django_permanent.managers import MultiPassThroughManager
#from notify.signals import notify

from payroll.models import EmployeeProfile, ServiceLine, Position

from decimal import Decimal

class Holiday(PermanentModel):
    name = models.CharField(max_length=64)
    date = models.DateField()
    recurring = models.BooleanField(default=True,
        help_text="The day is a holiday every year.")

    def __str__(self):
        return self.name

class LeavePeriod(PermanentModel):
    start_date = models.DateField()
    end_date = models.DateField()
    comment = models.TextField()

    def __str__(self):
        return "{} to {}".format(self.start_date, self.end_date)

def all_positions():
    return Position.objects.all()

def all_service_lines():
    return ServiceLine.objects.all()

class UserLeaveTypeQuerySet(PermanentQuerySet):
    def user_types(self, user=None, **kwargs):

        profile = user.profile
        q=self.filter(
                active=True,
                gender__in=['A', profile.gender],
                removed=None
            )
        exclude_types = []

        for type in q:
            if profile.service_line not in type.service_lines.all():
                exclude_types.append(type)
            if profile.position not in type.positions.all():
                exclude_types.append(type)

        q = q.exclude(pk__in=[type.pk for type in exclude_types])
        return q
UserLeaveTypeManager = UserLeaveTypeQuerySet.as_manager

class UserLeaveTypeManagerOld(models.Manager):
    def get_for_user(self, user_profile):
        exclude_types = []
        q = super(UserLeaveTypeManager, self).get_queryset().filter(
            active=True,
            gender__in=['A', user_profile.gender],
            removed=None
        )

        for type in q:
            if user_profile.service_line not in type.service_lines.all():
                exclude_types.append(type)
            if user_profile.position not in type.positions.all():
                exclude_types.append(type)

        return q.exclude(pk__in=[type.pk for type in exclude_types])

class LeaveType(PermanentModel):

    STATUS_CHOICES = ((0, 'Active'), (1, 'Inactive'))
    GENDER_CHOICES = (('A', 'Any'), ('M', 'Male'), ('F', 'Female'))

    class Meta:
        ordering = ('name', )

    name = models.CharField(max_length=64)
    no_of_days = models.DecimalField(max_digits=4, decimal_places=1, default=0,
        help_text="Maximum number of leave days within a leave period.")
    days_carried_forward = models.DecimalField(max_digits=4,
        decimal_places=1, default=0,
        help_text="If days from the previous leave periods are carried over, "
        "enter maximum number or percentage. 0 for None.")
    active = models.BooleanField(default=True)
    service_lines = models.ManyToManyField(ServiceLine,
        default=all_service_lines)
    positions = models.ManyToManyField(Position, default=all_positions)
    gender = models.CharField(max_length=2, choices=GENDER_CHOICES,
        blank=True, default='A')
    pay_percentage = models.DecimalField(max_digits=4,
        decimal_places=1, default=Decimal('100'))
    description = models.TextField(blank=True)

    objects = MultiPassThroughManager(UserLeaveTypeQuerySet, NonDeletedQuerySet)
#    objects = models.Manager()

    def __str__(self):
        return self.name

    def get_days_carried_forward(self, **kwargs):
        days = self.days_carried_forward
        if days == 0:
            return 0

        try:
            previous_period = LeavePeriod.objects.order_by('-id')[1]
        except:
            return 0
        else:
            bal = self.count_no_of_days_left(profile=kwargs.get('profile'),
                leave_period=previous_period)
            return days if days > bal else bal

    def count_no_of_days_left(self, **kwargs):

        requests = self.leave_requests.filter(
            profile=kwargs.get('profile'))
        leave_period_id = kwargs.get('leave_period_id')
        if leave_period_id:
            requests = requests.filter(leave_period_id=leave_period_id)
        else:
            leave_periods = LeavePeriod.objects.order_by('-id')
            if leave_periods:
                requests = requests.filter(leave_period=leave_periods[0])

        total = 0
        for r in requests:
            if r.is_past_due() is False and r.get_status() in ['P', 'A']:
                total += r.get_no_of_days()
        return self.no_of_days - total

class LeaveApprover(PermanentModel):
    profile = models.ForeignKey(EmployeeProfile, related_name="leave_approvers")

class LeaveRequestManager(models.Manager):
    def get_approvers(self):
        perm = Permission.objects.get(codename='hrp_handle_leave_requests')
        approvers = User.objects.filter(
            models.Q(models.Q(groups__permissions=perm)|
            models.Q(user_permissions=perm)),
            profile__isnull=False
        ).distinct()
        approver_profiles = list(EmployeeProfile.objects.filter(
            user__in=approvers))
        return approver_profiles


    def all_pending(self, **kwargs):

        apps=LeaveApplicationReview.objects.filter(leave_status='P',
            reviewer__in=[r.profile for r in LeaveApprover.objects.all()])
#            reviewer__in=self.get_approvers())
        q = super(LeaveRequestManager, self).get_queryset().filter(
            messages__in=apps)
        return q

    def all_accepted(self, **kwargs):

        reviews=LeaveApplicationReview.objects.filter(
            leave_status='A',
            reviewer__in=[r.profile for r in LeaveApprover.objects.all()])
#            reviewer__in=self.get_approvers())
        q = super(LeaveRequestManager, self).get_queryset().filter(
            messages__in=reviews)

        if kwargs.get('profile'):
            q = q.filter(profile=kwargs.get('profile'))

        return q

    def count_no_of_days_left(self, **kwargs):
        reviews=LeaveApplicationReview.objects.filter(leave_status__in=['P', 'A'],
#            reviewer__in=[r.profile for r in LeaveApprover.objects.all()])
            reviewer__in=self.get_approvers())
        leave_type = kwargs.get('leave_type')
        q = super(LeaveRequestManager, self).get_queryset().filter(
            profile=kwargs.get('profile'),
            leave_type=leave_type,
            messages__in=reviews
        )
        s=s
        total = 0
        for r in q:
            total += r.get_no_of_days()
        return leave_type.no_of_days - total

    def count_no_of_days_left_old(self, **kwargs):
        leave_type = kwargs.get('leave_type')
        q = super(LeaveRequestManager, self).get_queryset().filter(
            profile=kwargs.get('profile'),
            leave_type=leave_type

        )
        total = 0
        for r in q:
            if r.is_past_due() is False and r.get_status in ['P', 'A']:
                total += r.get_no_of_days()
        return leave_type.no_of_days - total

class LeaveRequest(PermanentModel):
    profile = models.ForeignKey(EmployeeProfile,
        related_name="leave_requests")
    leave_period = models.ForeignKey(LeavePeriod, related_name="leave_requests")
    leave_type = models.ForeignKey(LeaveType, related_name="leave_requests")
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField()
    no_of_days = models.DecimalField(max_digits=3, decimal_places=1,
        null=True, blank=True)
#    status = models.ForeignKey(LeaveRequestStatus, related_name="request")
    objects = LeaveRequestManager()

    def __str__(self):
        return "{}: {} to {}".format(self.leave_type, self.start_date,
            self.end_date)

    def get_approvers(self):
#        approvers = [r.profile for r in LeaveApprover.objects.all()]
        perm = Permission.objects.get(codename='hrp_handle_leave_requests')
        approvers = User.objects.filter(
            models.Q(models.Q(groups__permissions=perm)|
            models.Q(user_permissions=perm)),
            profile__isnull=False
        ).distinct()
        approver_profiles = list(EmployeeProfile.objects.filter(
            user__in=approvers))
        if self.profile.reports_to:
            approver_profiles.append(self.profile.reports_to)
        return set(approver_profiles)

    def is_past_due(self):
        if self.start_date < timezone.now().date():
            return True
        return False

    def get_status(self):
        '''Returns the latest review from any of the allowed leave approvers'''
        reviews=self.messages.filter(
#            reviewer__in=[r.profile for r in LeaveApprover.objects.all()]
            reviewer__in=self.get_approvers()
            ).order_by('id')
        review = 'P'
        for r in reviews:
            if r.leave_status != 'P':
                return r.leave_status

        if self.is_past_due():
            review = 'E' # Expired without
        return review

    def get_status_display(self):
        '''Returns the latest review from any of the allowed leave approvers'''
        reviews=self.messages.filter(
#            reviewer__in=[r.profile for r in LeaveApprover.objects.all()]
            reviewer__in=self.get_approvers()
            ).order_by('id')
        review = 'Pending'
        for r in reviews:
            if r.leave_status != 'P':
                return r.get_leave_status_display()

        if self.is_past_due():
            review = 'Expired' # Expired without review

        return review

    def get_no_of_days(self):

        hols = Holiday.objects.all()
        d = self.start_date - timezone.timedelta(1)
        no_of_days = 0
        weekend = set([5, 6])
        while(d <= self.end_date):
            d += timezone.timedelta(1)
            if d.weekday() in weekend or d in \
                [day.date for day in hols.filter(recurring=False)]:
                continue
            if d.strftime('%m%d') in \
                [day.date.strftime('%m%d') for day in hols.filter(recurring=True)]:
                continue
            no_of_days += 1
#        while(d <= self.end_date):
#            if d.weekday() not in weekend and d not in [day.date for day in hols.filter(rucurring=False)]:
#                no_of_days += 1
#            d += timezone.timedelta(1)

        return no_of_days

    def get_approved_by(self):
        review = self.messages.filter(leave_status='A')
        if review.exists():
            return review[0].reviewer

    def get_approve_comment(self):
        review = self.messages.filter(leave_status='A')
        if review.exists():
            return review[0].comment

    def get_approved_at(self):
        review = self.messages.filter(leave_status='A')
        if review.exists():
            return review[0].reviewed_at

    def notify_approvers(self):
        status = 0
        approvers = self.get_approvers()
        for approver in approvers:
            print ("notification to " + approver.get_fullname())
            app = self.messages.create(reviewer=approver)

            notify.send(
                'Leave',
                recipient=approver.user,
#                            actor=self.reviewer,
                actor_url=reverse('leave:leave_application_detail',
                    kwargs={'pk': app.id}),
                verb=' review request received from {}.'.format(self.profile.get_fullname()),
                actor_text='Leave',
                nf_type='leave'
            )

            email_message = getattr(settings,
                'LEAVE_REQUEST_RECEIVED_MESSAGE'
                            ).format(
                                employee = self.profile.get_fullname(),
                                leave_details = self,
                                approver = approver.get_fullname()
                            )
            try:
                approver.user.email_user(
                    getattr(settings, 'EMAIL_NOTIFICATION_SUBJECT_TEXT',
                        'HRP Notification'),
                    email_message,
                    from_email=settings.EMAIL_FROM_ADDRESS,
                    fail_silently=True
                )
            except:
                status = -1

        return status

    def notify_employee(self, **kwargs):
        status = 0

        email_message = kwargs.get('email_message', getattr(settings, 'LEAVE_REQUEST_SENT_MESSAGE'
            ).format(
                self.profile.get_fullname(),
                self
            )
        )
        try:
            self.profile.user.email_user(
                getattr(settings, 'EMAIL_NOTIFICATION_SUBJECT_TEXT',
                    'HRP Notification'),
                email_message,
                from_email=settings.EMAIL_FROM_ADDRESS
            )
        except:
            status = -1

        return status

class LeaveApplicationManager(models.Manager):
    def all_pending(self, **kwargs):

        profile = kwargs.get('profile')
        if profile:
            reviewers = [profile,]
        else:
#            reviewers = [r.profile for r in LeaveApprover.objects.all()]
            reviewers = self.get_approvers()
        apps=LeaveApplicationReview.objects.filter(leave_status='P',
            reviewer__in=reviewers)

        q = super(LeaveApplicationManager, self).get_queryset().filter(
            pk__in=[a.pk for a in apps])
        return q

    def all_applications(self, **kwargs):

        profile = kwargs.get('profile')
        if profile:
            reviewers = [profile,]
        else:
#            reviewers = [r.profile for r in LeaveApprover.objects.all()]
            reviewers = self.get_approvers()
#        apps=LeaveApplicationReview.objects.filter(leave_status='P',
#            reviewer__in=reviewers)

        q = super(LeaveApplicationManager, self).get_queryset().filter(
            reviewer__in=reviewers).order_by('-leave_status')
        return q

class LeaveApplicationReview(PermanentModel):
    STATUS_CHOICES = (('P', 'Pending'), ('A', 'Approved'), ('D', 'Denied'),
        ('C', 'Canceled'), ('E', 'Expired'))
    request = models.ForeignKey(LeaveRequest, related_name="messages")
    reviewer = models.ForeignKey(EmployeeProfile)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    comment = models.TextField(blank=True)
    leave_status = models.CharField(max_length=2, choices=STATUS_CHOICES,
        default='P')
    objects = LeaveApplicationManager()
