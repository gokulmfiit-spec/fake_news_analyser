"""Fetches and extracts readable article text from a submitted URL."""
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; FakeNewsVerifier/1.0)"}


class ScrapeError(Exception):
    pass


def fetch_article(url: str) -> dict:
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise ScrapeError(f"Could not fetch URL: {exc}") from exc

    soup = BeautifulSoup(response.text, "lxml")

    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else ""

    # Prefer <article> tag; fall back to all <p> tags.
    article_tag = soup.find("article")
    if article_tag:
        paragraphs = article_tag.find_all("p")
    else:
        paragraphs = soup.find_all("p")

    body = " ".join(p.get_text(" ", strip=True) for p in paragraphs)

    if not body or len(body) < 50:
        raise ScrapeError("Could not extract meaningful article text from this URL.")

    return {"title": title, "body": body, "url": url}
