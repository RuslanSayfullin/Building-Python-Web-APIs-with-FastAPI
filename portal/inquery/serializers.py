from rest_framework import serializers

from inquery.models import Inquery, Client


class InquerySerializer(serializers.ModelSerializer):
    class Meta:
        model =Inquery
        fields = ('uuid', 'description')

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ('name', 'phone')
