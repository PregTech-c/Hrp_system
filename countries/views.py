from rest_framework import viewsets, mixins
from countries.models import Country
from countries.serializers import CountrySerializer


class CountryViewSet(mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    """
    Returns list of countries with phone codes.
    """
    serializer_class = CountrySerializer
    queryset = Country.objects.all()
