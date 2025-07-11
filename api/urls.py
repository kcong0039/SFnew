# scanner_app/urls.py

from django.urls import path
from backend.views import scan_result

urlpatterns = [
    path("api/scan-result/", scan_result),
]