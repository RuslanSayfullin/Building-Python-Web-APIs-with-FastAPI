from django.urls import path

from inquery.views import DetailFrozeView, InqueryAPIView, ClientAPIView

urlpatterns = [
    path('', DetailFrozeView, name="calendar_today_url"),
    path('api/v1/inquerylist/', InqueryAPIView.as_view(), name="inquerylist"),
    path('api/v1/clientlist/', ClientAPIView.as_view(), name="clientlist"),
]
