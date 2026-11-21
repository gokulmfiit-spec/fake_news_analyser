from django.conf import settings
from django.db import models


class Submission(models.Model):
    TYPE_CHOICES = (
        ("text", "Text / Article"),
        ("url", "URL"),
        ("headline", "Headline"),
        ("social_post", "Social Media Post"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="submissions")
    submission_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="text")
    title = models.CharField(max_length=500, blank=True, default="")
    raw_content = models.TextField()
    source_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.submission_type}: {self.title or self.raw_content[:40]}"
