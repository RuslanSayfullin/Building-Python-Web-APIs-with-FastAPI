from django.urls import path

from inquery.views import DetailFrozeView

urlpatterns = [
    path('', DetailFrozeView, name="calendar_today_url"),
]
