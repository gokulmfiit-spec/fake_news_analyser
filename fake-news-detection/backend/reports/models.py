from django.db import models

from submissions.models import Submission


class VerificationReport(models.Model):
    LABEL_CHOICES = (
        ("real", "Likely Genuine"),
        ("fake", "Likely Fake"),
        ("uncertain", "Uncertain"),
    )

    submission = models.OneToOneField(
        Submission, on_delete=models.CASCADE, related_name="verification_report"
    )
    label = models.CharField(max_length=10, choices=LABEL_CHOICES)
    confidence_score = models.FloatField(help_text="0.0 to 1.0")
    flagged_statements = models.JSONField(default=list, blank=True)
    summary = models.TextField(blank=True, default="")
    supporting_sources = models.JSONField(default=list, blank=True)
    credibility_score = models.FloatField(null=True, blank=True)
    raw_signals = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Report #{self.id} ({self.label}, {self.confidence_score})"
