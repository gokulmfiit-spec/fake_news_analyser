from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from accounts.serializers import UserSerializer
from common.permissions import IsAdminRole
from reports.models import VerificationReport
from submissions.models import Submission

from .serializers import AdminReportSerializer


class AdminUserListView(generics.ListAPIView):
    """Module: Admin Dashboard — user management."""

    queryset = User.objects.all().order_by("-created_at")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]


class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Allows an admin to update a user's role or deactivate an account."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]


class AdminRecentReportsView(generics.ListAPIView):
    """Module: Admin Dashboard — content moderation feed of recent verifications."""

    queryset = VerificationReport.objects.select_related("submission", "submission__user").order_by("-created_at")
    serializer_class = AdminReportSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]


class AdminSummaryView(APIView):
    """Module: Admin Dashboard — top-line platform counts."""

    permission_classes = [permissions.IsAuthenticated, IsAdminRole]

    def get(self, request):
        return Response({
            "total_users": User.objects.count(),
            "total_submissions": Submission.objects.count(),
            "total_reports": VerificationReport.objects.count(),
            "fake_flagged": VerificationReport.objects.filter(label="fake").count(),
            "real_flagged": VerificationReport.objects.filter(label="real").count(),
            "uncertain_flagged": VerificationReport.objects.filter(label="uncertain").count(),
        })
