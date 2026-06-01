from django.urls import path

from .views import report, report_index

urlpatterns = [
    path("reports/", report_index, name="report-index"),
    path("reports/<str:name>/", report, name="report"),
]
