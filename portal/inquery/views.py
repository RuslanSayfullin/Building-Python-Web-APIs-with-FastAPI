from django.http import HttpResponse
from rest_framework import generics
from .models import Inquery, Client
from .serializers import InquerySerializer, ClientSerializer


def DetailFrozeView(request):
    return HttpResponse("Страница с деталями заявки")

class InqueryAPIView(generics.ListAPIView):
    """Предоставляет список, заявок"""
    queryset = Inquery.objects.all()
    serializer_class = InquerySerializer

class ClientAPIView(generics.ListAPIView):
    """Предоставляет список, клиентов"""
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


