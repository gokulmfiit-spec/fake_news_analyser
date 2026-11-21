from django.urls import path

from .views import (
    AdminRecentReportsView,
    AdminSummaryView,
    AdminUserDetailView,
    AdminUserListView,
)

urlpatterns = [
    path("summary/", AdminSummaryView.as_view(), name="admin-summary"),
    path("users/", AdminUserListView.as_view(), name="admin-users"),
    path("users/<int:pk>/", AdminUserDetailView.as_view(), name="admin-user-detail"),
    path("reports/", AdminRecentReportsView.as_view(), name="admin-recent-reports"),
]
