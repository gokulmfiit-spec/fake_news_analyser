from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/submissions/", include("submissions.urls")),
    path("api/reports/", include("reports.urls")),
    path("api/feedback/", include("feedback.urls")),
    path("api/analytics/", include("analytics.urls")),
    path("api/admin-panel/", include("admin_panel.urls")),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
