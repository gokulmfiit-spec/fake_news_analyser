"""NLP preprocessing utilities shared across the AI pipeline."""
import re

SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
WHITESPACE_RE = re.compile(r"\s+")
URL_RE = re.compile(r"https?://\S+")


def clean_text(text: str) -> str:
    """Normalize whitespace and strip stray control characters."""
    if not text:
        return ""
    text = text.replace("\r", " ").replace("\n", " ")
    text = WHITESPACE_RE.sub(" ", text).strip()
    return text


def split_sentences(text: str):
    """Lightweight sentence splitter (avoids heavy NLP dependencies)."""
    text = clean_text(text)
    if not text:
        return []
    sentences = SENTENCE_SPLIT_RE.split(text)
    return [s.strip() for s in sentences if len(s.strip()) > 3]


def extract_domain(url: str) -> str:
    match = re.search(r"https?://(?:www\.)?([^/]+)", url or "")
    return match.group(1).lower() if match else ""
