"""
Orchestrates the full AI Fake News Detection pipeline:

  1. Preprocess text
  2. ML/heuristic classification
  3. LLM verdict + suspicious-statement extraction + summary
  4. Source credibility analysis (if a URL was submitted)
  5. Combine into one final result used to populate VerificationReport

This is the single entry point the `submissions` and `reports` apps call.
"""
from . import credibility
from .classifier import get_classifier
from .llm_client import get_llm_verdict
from .preprocessing import clean_text

# Weights for blending signals into the final confidence score.
WEIGHT_ML = 0.45
WEIGHT_LLM = 0.40
WEIGHT_CREDIBILITY = 0.15

LABEL_TO_SCORE = {"real": 1.0, "uncertain": 0.5, "fake": 0.0}


def _label_from_score(score: float) -> str:
    if score >= 0.6:
        return "real"
    if score <= 0.4:
        return "fake"
    return "uncertain"


def analyze_content(text: str, source_url: str = "") -> dict:
    """
    Returns a dict matching the VerificationReport model fields:
    label, confidence_score, flagged_statements, summary, supporting_sources,
    credibility_score
    """
    cleaned = clean_text(text)

    # 1. ML / heuristic classification
    ml_result = get_classifier().predict(cleaned)
    ml_score = LABEL_TO_SCORE.get(ml_result["label"], 0.5)

    # 2. LLM verdict (optional — degrades gracefully if unavailable)
    llm_result = get_llm_verdict(cleaned)
    if llm_result.get("available"):
        llm_score = LABEL_TO_SCORE.get(llm_result.get("verdict"), 0.5)
        llm_confidence = llm_result.get("confidence") or 0.5
    else:
        llm_score = 0.5
        llm_confidence = 0.0  # contributes no weight if unavailable

    # 3. Source credibility (only meaningful for URL submissions)
    cred_result = None
    cred_score = 0.5
    if source_url:
        headline_guess = cleaned[:120]
        cred_result = credibility.analyze_source(source_url, headline_guess)
        cred_score = cred_result["credibility_score"]

    # Re-normalize weights if LLM is unavailable so ML+credibility fill the gap
    weight_ml, weight_llm, weight_cred = WEIGHT_ML, WEIGHT_LLM, WEIGHT_CREDIBILITY
    if not llm_result.get("available"):
        weight_ml += weight_llm * 0.7
        weight_cred += weight_llm * 0.3
        weight_llm = 0
    if not source_url:
        weight_ml += weight_cred * 0.6
        weight_llm += weight_cred * 0.4
        weight_cred = 0

    combined_score = (
        ml_score * weight_ml
        + llm_score * weight_llm
        + cred_score * weight_cred
    )
    final_label = _label_from_score(combined_score)

    # Confidence: blend classifier confidence and (if available) LLM confidence
    confidences = [ml_result["confidence"]]
    if llm_result.get("available"):
        confidences.append(llm_confidence)
    final_confidence = round(sum(confidences) / len(confidences), 2)

    flagged_statements = list(ml_result.get("signals", []))
    if llm_result.get("available"):
        flagged_statements += llm_result.get("suspicious_statements", [])

    summary_parts = []
    if llm_result.get("available"):
        summary_parts.append(llm_result.get("summary", ""))
    else:
        summary_parts.append(
            "Automated summary based on rule-based/ML signals only "
            "(LLM verification was not available for this analysis)."
        )
    if cred_result:
        summary_parts.append(
            f"Source domain '{cred_result['domain']}' is rated "
            f"'{cred_result['label']}' for credibility."
        )

    return {
        "label": final_label,
        "confidence_score": final_confidence,
        "flagged_statements": flagged_statements,
        "summary": " ".join(p for p in summary_parts if p),
        "supporting_sources": (cred_result or {}).get("related_coverage", []),
        "credibility_score": cred_score if source_url else None,
        "raw_signals": {
            "ml": ml_result,
            "llm": llm_result,
            "credibility": cred_result,
        },
    }
