from rest_framework import serializers

from reports.models import VerificationReport


class AdminSubmissionMiniSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    source_url = serializers.CharField(allow_null=True)
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        return {"username": obj.user.username}


class AdminReportSerializer(serializers.ModelSerializer):
    submission = serializers.SerializerMethodField()

    class Meta:
        model = VerificationReport
        fields = ("id", "submission", "label", "confidence_score", "created_at")

    def get_submission(self, obj):
        s = obj.submission
        return {
            "id": s.id,
            "title": s.title,
            "source_url": s.source_url,
            "user": {"username": s.user.username},
        }
