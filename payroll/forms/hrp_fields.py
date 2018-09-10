__author__ = "Steven Kawuma <kawuma@gmail.com>"
__date__ = "Jan 4, 2017 6:40:49 PM"

from django.forms import ModelChoiceField
from payroll.models import EmployeeProfile

class EmployeeModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s (%s)" % (obj.get_fullname(), obj.position)

class UserModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):

        try:
            profile = obj.profile
            return "%s (%s)" % (profile.get_fullname(), profile.position)
        except EmployeeProfile.DoesNotExist:
            return "%s" % (obj.username)

class EmployeeChoiceField(ModelChoiceField):
    
    def __init__(self, obj_label=None, *args, **kwargs):
        super(EmployeeChoiceField, self).__init__(self, *args, **kwargs)
        self.queryset = EmployeeProfile.objects.order_by('user__last_name')
        self.obj_label = obj_label
        self.empty_label = '-- All --'
        self.required = False
    
    def label_from_instance(self, obj):
        return "{} ({})".format(obj.get_fullname(), obj.position)


class ServiceLineChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
#        return "{} - {}".format(obj.name, obj.service_line_type)
        return obj.get_name()