from payroll.models import employee_models
from django.contrib.auth.models import User
from django.db.models import Q, Max

def run():
    u = User.objects.get(username='richo')
    q = Q(employee_appraisal__status__in=['3',])
    c=Q()
    q = u.profile.appraisal_receipts.filter(c).values('employee_appraisal', 'id').annotate(pk=Max('id'))
    print q

    appraisals = {}
    for i in u.profile.appraisal_receipts.filter(c).values('employee_appraisal', 'id').order_by('id'):
        appraisals[str(i['employee_appraisal'])] = i['id']
        print i['employee_appraisal'], i['id']
    print appraisals.itervalues()
