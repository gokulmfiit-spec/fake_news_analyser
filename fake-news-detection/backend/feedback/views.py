from rest_framework import generics, permissions

from .models import Feedback
from .serializers import FeedbackSerializer


class FeedbackCreateView(generics.CreateAPIView):
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]


class FeedbackListView(generics.ListAPIView):
    """Admins see all feedback; regular users see only their own."""

    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.role == "admin":
            return Feedback.objects.all()
        return Feedback.objects.filter(user=user)
