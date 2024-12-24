from django.contrib import admin
from django.urls import path

from test_weenat.views import IngestView, DataView, SummaryView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/ingest', IngestView.as_view(), name='ingest'),
    path('api/summary', SummaryView.as_view(), name='summary'),
    path('api/data', DataView.as_view(), name='data'),
]
