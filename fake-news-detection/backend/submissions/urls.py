from django.urls import path

from .views import SubmissionHistoryView, SubmitTextView, SubmitURLView

urlpatterns = [
    path("text/", SubmitTextView.as_view(), name="submit-text"),
    path("url/", SubmitURLView.as_view(), name="submit-url"),
    path("history/", SubmissionHistoryView.as_view(), name="submission-history"),
]
