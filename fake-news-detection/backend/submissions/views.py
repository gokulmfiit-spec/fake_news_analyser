from django.db import transaction
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from ai_engine.pipeline import analyze_content
from reports.models import VerificationReport
from reports.serializers import VerificationReportSerializer

from .models import Submission
from .scraper import ScrapeError, fetch_article
from .serializers import SubmissionListSerializer


def _run_pipeline_and_save(submission: Submission, text: str, source_url: str = "") -> VerificationReport:
    result = analyze_content(text, source_url=source_url)
    report = VerificationReport.objects.create(
        submission=submission,
        label=result["label"],
        confidence_score=result["confidence_score"],
        flagged_statements=result["flagged_statements"],
        summary=result["summary"],
        supporting_sources=result["supporting_sources"],
        credibility_score=result["credibility_score"],
        raw_signals=result["raw_signals"],
    )
    return report


class SubmitTextView(APIView):
    """Module: News Article Submission (also handles headline / social post text)."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        submission_type = request.data.get("submission_type", "text")
        title = request.data.get("title", "")
        raw_content = request.data.get("raw_content", "")

        if not raw_content or not raw_content.strip():
            return Response({"detail": "raw_content is required."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            submission = Submission.objects.create(
                user=request.user,
                submission_type=submission_type,
                title=title,
                raw_content=raw_content,
            )
            report = _run_pipeline_and_save(submission, raw_content)

        return Response(VerificationReportSerializer(report).data, status=status.HTTP_201_CREATED)


class SubmitURLView(APIView):
    """Module: URL Verification."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        url = request.data.get("source_url", "").strip()
        if not url:
            return Response({"detail": "source_url is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            article = fetch_article(url)
        except ScrapeError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        with transaction.atomic():
            submission = Submission.objects.create(
                user=request.user,
                submission_type="url",
                title=article["title"],
                raw_content=article["body"],
                source_url=url,
            )
            report = _run_pipeline_and_save(submission, article["body"], source_url=url)

        return Response(VerificationReportSerializer(report).data, status=status.HTTP_201_CREATED)


class SubmissionHistoryView(generics.ListAPIView):
    """Module: News Search and History."""

    serializer_class = SubmissionListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["submission_type"]
    search_fields = ["title", "raw_content", "source_url"]

    def get_queryset(self):
        qs = Submission.objects.filter(user=self.request.user).select_related("verification_report")
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(title__icontains=search) | qs.filter(raw_content__icontains=search)
        label = self.request.query_params.get("label")
        if label:
            qs = qs.filter(verification_report__label=label)
        return qs.order_by("-created_at")
