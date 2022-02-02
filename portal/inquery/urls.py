from django.urls import path

from inquery.views import DetailFrozeView

urlpatterns = [
    path('', DetailFrozeView, name="detail_froze_url"),
]
