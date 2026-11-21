from django.conf import settings
from django.db import models

from reports.models import VerificationReport


class Feedback(models.Model):
    report = models.ForeignKey(VerificationReport, on_delete=models.CASCADE, related_name="feedback_entries")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="feedback_entries")
    is_helpful = models.BooleanField()
    was_accurate = models.BooleanField(null=True, blank=True, help_text="User's opinion on whether the verdict was correct")
    comment = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("report", "user")

    def __str__(self):
        return f"Feedback on report #{self.report_id} by {self.user}"
