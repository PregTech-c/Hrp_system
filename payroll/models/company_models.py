__author__ = "Steven Kawuma <kawuma@gmail.com>"
__date__ = "Jan 22, 2017 10:15:00 AM"

from django.db import models
from django_permanent.models import PermanentModel

class ServiceLineType(PermanentModel):
    class Meta:
    	ordering = ['name']

    name = models.CharField(max_length=32, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class ServiceLine(PermanentModel):
    class Meta:
    	ordering = ['name']

    name = models.CharField(max_length=32, unique=True)
    service_line_type = models.ForeignKey(ServiceLineType, related_name='lines')
    parent_service_line = models.ForeignKey('self', null=True, blank=True)

    def __str__(self):

        return self.name

    def get_name(self):
        name = self.name
        if self.parent_service_line is not None:
            return "{} / {}".format(self.parent_service_line.get_name(), name)
        else:
            return name
