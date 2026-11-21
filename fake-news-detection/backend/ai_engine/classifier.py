"""
ML classification layer.

Two modes:
1. If a trained model exists at settings.ML_MODEL_PATH (produced by
   `train_baseline.py`), it is loaded once and used for TF-IDF + Logistic
   Regression predictions.
2. Otherwise, falls back to a transparent rule-based heuristic scorer so the
   system is fully functional out of the box with zero training data,
   and swappable later without changing any calling code.

Replace `HeuristicClassifier` or point ML_MODEL_PATH at a fine-tuned
HuggingFace/sklearn model to upgrade prediction quality later.
"""
import os
import re

from django.conf import settings

CLICKBAIT_PHRASES = [
    "you won't believe", "shocking", "doctors hate", "what happens next",
    "goes viral", "number 7 will", "this one trick", "share before it's deleted",
    "mainstream media won't tell you", "wake up", "they don't want you to know",
    "breaking:", "urgent:", "must see", "miracle cure", "secret they hid",
]

SENSATIONAL_WORDS = [
    "outrageous", "unbelievable", "terrifying", "explosive", "bombshell",
    "destroyed", "annihilated", "slammed", "devastating", "shocking",
]

HEDGE_WORDS = ["reportedly", "allegedly", "sources say", "some say", "it is claimed"]


class HeuristicClassifier:
    """Rule-based fallback classifier (no training data required)."""

    def predict(self, text: str):
        if not text or len(text.strip()) < 20:
            return {"label": "uncertain", "confidence": 0.5, "signals": ["Text too short to assess reliably."]}

        lower = text.lower()
        signals = []
        suspicion_score = 0.0  # 0 = looks genuine, 1 = looks fake

        # Clickbait phrase detection
        clickbait_hits = [p for p in CLICKBAIT_PHRASES if p in lower]
        if clickbait_hits:
            suspicion_score += 0.25
            signals.append(f"Contains clickbait-style phrasing ({', '.join(clickbait_hits[:3])}).")

        # Sensational language density
        sensational_hits = sum(lower.count(w) for w in SENSATIONAL_WORDS)
        if sensational_hits:
            weight = min(0.2, 0.05 * sensational_hits)
            suspicion_score += weight
            signals.append("Uses heavily sensational/emotional language.")

        # Excessive capitalization
        cap_words = re.findall(r"\b[A-Z]{4,}\b", text)
        if len(cap_words) >= 3:
            suspicion_score += 0.15
            signals.append("Unusually frequent ALL-CAPS words (common in misleading posts).")

        # Excessive punctuation (!!! or ???)
        if re.search(r"[!?]{2,}", text):
            suspicion_score += 0.1
            signals.append("Excessive exclamation/question marks.")

        # Hedging without attribution
        hedge_hits = [w for w in HEDGE_WORDS if w in lower]
        if hedge_hits:
            suspicion_score += 0.1
            signals.append("Uses vague attribution (e.g. 'sources say') without naming a source.")

        # Lack of any numbers/dates/named entities as a weak proxy for verifiability
        if not re.search(r"\d", text):
            suspicion_score += 0.05
            signals.append("No dates, statistics, or figures included to support claims.")

        # Very short "article" pretending to be full news
        word_count = len(text.split())
        if word_count < 40:
            suspicion_score += 0.1
            signals.append("Very short for a news article; lacks supporting detail.")

        suspicion_score = max(0.0, min(1.0, suspicion_score))

        if suspicion_score >= 0.55:
            label = "fake"
            confidence = round(0.5 + suspicion_score / 2, 2)
        elif suspicion_score <= 0.2:
            label = "real"
            confidence = round(0.5 + (0.3 - suspicion_score), 2)
            confidence = min(confidence, 0.85)
        else:
            label = "uncertain"
            confidence = round(0.5 + abs(0.35 - suspicion_score) * 0.3, 2)

        if not signals:
            signals.append("No strong misinformation indicators detected by the heuristic scorer.")

        return {"label": label, "confidence": min(confidence, 0.97), "signals": signals}


class TrainedModelClassifier:
    """Wraps a joblib-persisted sklearn Pipeline (TF-IDF + LogisticRegression)."""

    def __init__(self, model_path):
        import joblib

        self.pipeline = joblib.load(model_path)
        self.classes_ = list(self.pipeline.classes_)

    def predict(self, text: str):
        proba = self.pipeline.predict_proba([text])[0]
        idx = proba.argmax()
        label = self.classes_[idx]
        confidence = round(float(proba[idx]), 2)
        return {
            "label": label,
            "confidence": confidence,
            "signals": [f"ML model (TF-IDF + Logistic Regression) predicted '{label}'."],
        }


_classifier_instance = None


def get_classifier():
    """Returns a cached classifier instance: trained model if available, else heuristic."""
    global _classifier_instance
    if _classifier_instance is not None:
        return _classifier_instance

    model_path = getattr(settings, "ML_MODEL_PATH", None)
    if model_path and os.path.exists(model_path):
        try:
            _classifier_instance = TrainedModelClassifier(model_path)
            return _classifier_instance
        except Exception:
            pass  # fall through to heuristic on any load failure

    _classifier_instance = HeuristicClassifier()
    return _classifier_instance
