from __future__ import unicode_literals

from django_permanent.models import PermanentModel
from django.db import models
from django.contrib.auth.models import User

class IdType(PermanentModel):
    class Permanent:
        restore_on_create = True
    description = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.description

class AssetStatus(PermanentModel):
    description = models.CharField(max_length=64)

    def __str__(self):
        return self.description

class Category(PermanentModel):
    class Meta:
        verbose_name_plural = "Categories"
    class Permanent:
        restore_on_create = True

    name = models.CharField(max_length=32, unique=True)
    description = models.CharField(max_length=256, null=True, blank=True)

    def __str__(self):
        return self.name

class Asset(PermanentModel):
    category = models.ForeignKey(Category, related_name='assets')
    model = models.CharField(max_length=32)
    id_type = models.ForeignKey(IdType)
    id_number = models.CharField(max_length=32)
    date_of_manufacture = models.DateTimeField(null=True, blank=True)
    description = models.CharField(max_length=256, null=True)

    def get_current_issue(self):
        try:
            return self.issues.filter(returned_date__isnull=True)[0]
        except:
            return None

    def get_id(self):
        return "{}/{}".format(self.id_type, self.id_number)

    def __str__(self):
        return "{} {}".format(self.category.name, self.get_id())
    
class AssetIssuance(PermanentModel):

    asset = models.ForeignKey(Asset, related_name='issues')
    employee = models.ForeignKey(User, null=True)
    assignment_date = models.DateTimeField(auto_now_add=True)
    returned_date = models.DateTimeField(null=True)
    comment = models.TextField()
    asset_status = models.ForeignKey(AssetStatus, related_name='issues',
        default=1)
