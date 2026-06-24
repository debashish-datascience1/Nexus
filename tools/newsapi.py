import re
import urllib.parse
import feedparser
from config import NEWSAPI_KEY


def _clean_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "").strip()


def fetch_news(query: str, page_size: int = 10) -> list[dict]:
    """NewsAPI — richer descriptions and images when API key is present."""
    if not NEWSAPI_KEY:
        return []
    try:
        from newsapi import NewsApiClient
        client = NewsApiClient(api_key=NEWSAPI_KEY)
        resp = client.get_everything(
            q=query, language="en", sort_by="publishedAt", page_size=page_size
        )
        results = []
        for a in resp.get("articles", []):
            if not a.get("title"):
                continue
            desc = a.get("description") or a.get("content") or ""
            results.append({
                "title": a["title"],
                "source": a["source"]["name"],
                "published": (a["publishedAt"] or "")[:10],
                "url": a["url"],
                "description": desc[:500],
                "image_url": a.get("urlToImage") or "",
            })
        return results
    except Exception:
        return []


def fetch_rss(query: str, num: int = 10) -> list[dict]:
    """Google News RSS — query-based, covers any topic worldwide, no key needed."""
    encoded = urllib.parse.quote_plus(query)
    url = f"https://news.google.com/rss/search?q={encoded}&hl=en&gl=US&ceid=US:en"
    try:
        feed = feedparser.parse(url)
        results = []
        for entry in feed.entries[:num]:
            title = entry.get("title", "")

            # Google News embeds source in the title: "Headline - Source Name"
            source = ""
            if hasattr(entry, "source") and entry.source:
                source = entry.source.get("title", "")
            if not source and " - " in title:
                parts = title.rsplit(" - ", 1)
                title = parts[0].strip()
                source = parts[1].strip()

            description = _clean_html(entry.get("summary", ""))
            if description == title:
                description = ""

            results.append({
                "title": title,
                "source": source or "News",
                "published": (entry.get("published", "") or "")[:16],
                "url": entry.get("link", ""),
                "description": description[:600],
                "image_url": "",
            })
        return results
    except Exception:
        return []
