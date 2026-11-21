"""
Source credibility analysis.

Starts as a maintainable heuristic domain list (extend freely). Optionally
layers a Trusted News API lookup on top if TRUSTED_NEWS_API_KEY is set, to
check whether the same story is being reported by known outlets.
"""
import requests
from django.conf import settings

from .preprocessing import extract_domain

# NOTE: illustrative starter lists only — extend/curate for production use.
RELIABLE_DOMAINS = {
    "reuters.com", "apnews.com", "bbc.com", "bbc.co.uk", "npr.org",
    "theguardian.com", "nytimes.com", "washingtonpost.com", "thehindu.com",
    "indianexpress.com", "hindustantimes.com", "ndtv.com", "pib.gov.in",
}

KNOWN_UNRELIABLE_DOMAINS = {
    # Example placeholders — replace with a curated fact-checked list
    # (e.g. from MediaBiasFactCheck-style datasets) before production use.
    "example-fake-news-site.com",
    "totallyrealnews.biz",
}


def score_domain(domain: str) -> dict:
    domain = (domain or "").lower().replace("www.", "")
    if not domain:
        return {"domain": domain, "credibility_score": 0.5, "label": "unknown", "note": "No URL/domain provided."}

    if domain in RELIABLE_DOMAINS:
        return {"domain": domain, "credibility_score": 0.9, "label": "reliable",
                "note": "Recognized as an established news source."}

    if domain in KNOWN_UNRELIABLE_DOMAINS:
        return {"domain": domain, "credibility_score": 0.1, "label": "unreliable",
                "note": "Flagged in the known-unreliable domain list."}

    return {"domain": domain, "credibility_score": 0.5, "label": "unknown",
            "note": "Domain not in the curated reputation list; treat with neutral caution."}


def cross_check_trusted_news(query: str, max_results: int = 5) -> list:
    """Optional: search a trusted news API for related coverage of the topic."""
    api_key = getattr(settings, "TRUSTED_NEWS_API_KEY", "")
    if not api_key or not query:
        return []

    try:
        response = requests.get(
            settings.TRUSTED_NEWS_API_URL,
            params={"q": query[:300], "pageSize": max_results, "sortBy": "relevancy", "apiKey": api_key},
            timeout=15,
        )
        response.raise_for_status()
        articles = response.json().get("articles", [])
        return [
            {
                "title": a.get("title"),
                "source": (a.get("source") or {}).get("name"),
                "url": a.get("url"),
                "published_at": a.get("publishedAt"),
            }
            for a in articles[:max_results]
        ]
    except Exception:
        return []


def analyze_source(url: str, headline_for_search: str = "") -> dict:
    domain = extract_domain(url)
    domain_result = score_domain(domain)
    related_coverage = cross_check_trusted_news(headline_for_search or domain)
    domain_result["related_coverage"] = related_coverage
    return domain_result
