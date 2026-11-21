from django.db.models import Avg, Count
from django.db.models.functions import TruncDate
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from feedback.models import Feedback
from reports.models import VerificationReport
from submissions.models import Submission


class OverviewAnalyticsView(APIView):
    """
    Module: Reports & Analytics Dashboard.
    Scoped to the current user unless they are an admin, in which case it
    returns platform-wide stats.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        is_admin = user.is_superuser or user.role == "admin"

        submissions_qs = Submission.objects.all() if is_admin else Submission.objects.filter(user=user)
        reports_qs = VerificationReport.objects.all() if is_admin else VerificationReport.objects.filter(submission__user=user)

        label_counts = reports_qs.values("label").annotate(count=Count("id"))
        by_type = submissions_qs.values("submission_type").annotate(count=Count("id"))

        trend = (
            submissions_qs.annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )

        avg_confidence = reports_qs.aggregate(avg=Avg("confidence_score"))["avg"]

        top_flagged_domains = (
            submissions_qs.exclude(source_url__isnull=True)
            .exclude(source_url="")
            .values("source_url")
            .annotate(count=Count("id"))
            .order_by("-count")[:5]
        )

        feedback_qs = Feedback.objects.all() if is_admin else Feedback.objects.filter(user=user)
        helpful_ratio = None
        total_feedback = feedback_qs.count()
        if total_feedback:
            helpful_ratio = round(feedback_qs.filter(is_helpful=True).count() / total_feedback, 2)

        return Response({
            "scope": "platform" if is_admin else "personal",
            "total_submissions": submissions_qs.count(),
            "total_reports": reports_qs.count(),
            "label_breakdown": list(label_counts),
            "submission_type_breakdown": list(by_type),
            "daily_trend": list(trend),
            "average_confidence": round(avg_confidence, 2) if avg_confidence else None,
            "top_submitted_sources": list(top_flagged_domains),
            "feedback_helpful_ratio": helpful_ratio,
            "total_feedback": total_feedback,
        })
