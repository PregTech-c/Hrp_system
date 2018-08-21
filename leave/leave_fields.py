from django.forms import ModelChoiceField
from leave.models import Country


class CountryChoiceField(ModelChoiceField):

    def label_from_instance(self, obj):
    #    return "{} - {}".format(obj.name)
        return obj.name
