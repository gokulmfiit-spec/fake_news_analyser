from rest_framework import serializers

from submissions.serializers import SubmissionCreateSerializer

from .models import VerificationReport


class VerificationReportSerializer(serializers.ModelSerializer):
    submission = SubmissionCreateSerializer(read_only=True)

    class Meta:
        model = VerificationReport
        fields = (
            "id", "submission", "label", "confidence_score", "flagged_statements",
            "summary", "supporting_sources", "credibility_score", "created_at",
        )
