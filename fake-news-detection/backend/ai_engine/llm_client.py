"""
Thin wrapper around an LLM API (Anthropic-compatible /v1/messages endpoint
by default) used to produce a natural-language verdict, flagged suspicious
statements, and a plain-language summary.

If settings.LLM_API_KEY is empty, `get_llm_verdict` returns a clearly-marked
unavailable result instead of raising, so the rest of the pipeline keeps
working with just the ML/heuristic signal.
"""
import json

import requests
from django.conf import settings

PROMPT_TEMPLATE = """You are a fact-verification assistant for a fake news detection platform.
Analyze the following content and respond ONLY with valid JSON (no markdown fences, no preamble)
matching this exact schema:

{{
  "verdict": "real" | "fake" | "uncertain",
  "confidence": <float between 0 and 1>,
  "suspicious_statements": [<list of up to 5 short exact quotes or claims from the text that seem misleading, unverifiable, or exaggerated>],
  "summary": "<2-3 sentence plain-language explanation of the verdict>"
}}

Content to analyze:
\"\"\"
{content}
\"\"\"
"""


def get_llm_verdict(text: str) -> dict:
    api_key = getattr(settings, "LLM_API_KEY", "")
    if not api_key:
        return {
            "available": False,
            "verdict": None,
            "confidence": None,
            "suspicious_statements": [],
            "summary": "LLM verification unavailable: no LLM_API_KEY configured. "
                       "Set LLM_API_KEY in backend/.env to enable this feature.",
        }

    prompt = PROMPT_TEMPLATE.format(content=text[:6000])

    try:
        response = requests.post(
            settings.LLM_API_URL,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": settings.LLM_MODEL,
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        text_blocks = [b["text"] for b in data.get("content", []) if b.get("type") == "text"]
        raw = "".join(text_blocks).strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(raw)
        parsed["available"] = True
        return parsed
    except Exception as exc:  # network error, bad JSON, non-2xx, etc.
        return {
            "available": False,
            "verdict": None,
            "confidence": None,
            "suspicious_statements": [],
            "summary": f"LLM verification failed: {exc}",
        }
