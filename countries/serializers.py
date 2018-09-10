from rest_framework import serializers
from countries.models import Country


class CountrySerializer(serializers.ModelSerializer):

    class Meta:
        model = Country
        fields = ('id', 'name', 'code')
