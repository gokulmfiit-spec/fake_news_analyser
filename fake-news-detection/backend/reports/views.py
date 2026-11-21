from rest_framework import generics, permissions

from common.permissions import IsOwnerOrAdmin

from .models import VerificationReport
from .serializers import VerificationReportSerializer


class ReportDetailView(generics.RetrieveAPIView):
    queryset = VerificationReport.objects.select_related("submission", "submission__user")
    serializer_class = VerificationReportSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_object(self):
        obj = super().get_object()
        return obj

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.role == "admin":
            return VerificationReport.objects.all()
        return VerificationReport.objects.filter(submission__user=user)
