from rest_framework import serializers

from .models import Submission


class SubmissionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ("id", "submission_type", "title", "raw_content", "source_url", "created_at")
        read_only_fields = ("id", "created_at")

    def validate(self, attrs):
        sub_type = attrs.get("submission_type")
        if sub_type == "url" and not attrs.get("source_url"):
            raise serializers.ValidationError("source_url is required for submission_type='url'.")
        if sub_type != "url" and not attrs.get("raw_content"):
            raise serializers.ValidationError("raw_content is required for text/headline/social_post submissions.")
        return attrs


class SubmissionListSerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField()
    confidence_score = serializers.SerializerMethodField()
    report_id = serializers.SerializerMethodField()

    class Meta:
        model = Submission
        fields = (
            "id", "submission_type", "title", "source_url", "created_at",
            "label", "confidence_score", "report_id",
        )

    def get_report(self, obj):
        return getattr(obj, "verification_report", None)

    def get_label(self, obj):
        report = self.get_report(obj)
        return report.label if report else None

    def get_confidence_score(self, obj):
        report = self.get_report(obj)
        return report.confidence_score if report else None

    def get_report_id(self, obj):
        report = self.get_report(obj)
        return report.id if report else None
