from __future__ import unicode_literals

from django.db import models


class Country(models.Model):
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=10)

    def __str__(self):
        return '{}'.format(self.name)

    class Meta:
        ordering = ('name',)
