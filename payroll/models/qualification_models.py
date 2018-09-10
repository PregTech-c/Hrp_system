__author__ = "Steven Kawuma <kawuma@gmail.com>"
__date__ = "Jan 18, 2017 6:21:06 AM"

from django.db import models
from django.utils.translation import gettext as _
from django_permanent.models import PermanentModel

class EducationLevel(PermanentModel):

    EDUC_LEVEL_CHOICES = (
        (_("PRIMARY"), _("Primary")),
        (_("OLEVEL"), _("O'Level")),
        (_("ALEVEL"), _("A'Level")),
        (_("TERTIARY"), _("Tertiary")),
        (_("UNIVERSITY"), _("University")),
    )

    class Meta:
        ordering = ("id",)
        unique_together = (("level", "qualification"),)

    level = models.CharField(max_length=16, choices=EDUC_LEVEL_CHOICES)
    qualification = models.CharField(max_length=512, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return "{}/{}".format(self.get_level_display(), self.qualification)
#    def __unicode__(self):
#        return self.get_level_display
#
class Skill(PermanentModel):

    name = models.CharField(max_length=512)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Language(PermanentModel):

    name = models.CharField(max_length=512, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Certification(PermanentModel):

    class Permanent:
        restore_on_create = True

    name = models.CharField(max_length=512)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Membership(PermanentModel):

    name = models.CharField(max_length=512)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
