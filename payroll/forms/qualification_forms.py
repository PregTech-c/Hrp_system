__author__ = "Steven Kawuma <kawuma@gmail.com>"
__date__ = "Jan 24, 2017 5:21:27 AM"
from django.forms import *

from payroll.models.qualification_models import *

class EducationLevelForm(ModelForm):

    class Meta:
        model = EducationLevel
        exclude = ()

class SkillForm(ModelForm):
    
    class Meta:
        model = Skill
        exclude = ()

class CertificationForm(ModelForm):
    
    class Meta:
        model = Certification
        exclude = ()

class MembershipForm(ModelForm):
    
    class Meta:
        model = Membership
        exclude = ()

class LanguageForm(ModelForm):
    
    class Meta:
        model = Language
        exclude = ()
