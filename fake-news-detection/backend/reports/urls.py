from django.urls import path

from .views import ReportDetailView

urlpatterns = [
    path("<int:pk>/", ReportDetailView.as_view(), name="report-detail"),
]
