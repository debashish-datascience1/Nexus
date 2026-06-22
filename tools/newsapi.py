import feedparser
from config import NEWSAPI_KEY

RSS_FEEDS = [
    "https://hnrss.org/frontpage",
    "https://feeds.feedburner.com/TechCrunch",
    "https://www.theverge.com/rss/index.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
]


def fetch_news(query: str) -> list[dict]:
    """Try NewsAPI first; returns [] if key is missing or quota is hit."""
    if not NEWSAPI_KEY:
        return []
    try:
        from newsapi import NewsApiClient
        client = NewsApiClient(api_key=NEWSAPI_KEY)
        resp = client.get_everything(
            q=query, language="en", sort_by="publishedAt", page_size=5
        )
        return [
            {
                "title": a["title"],
                "source": a["source"]["name"],
                "published": (a["publishedAt"] or "")[:10],
                "url": a["url"],
                "description": a.get("description", ""),
            }
            for a in resp.get("articles", [])
            if a.get("title")
        ]
    except Exception:
        return []


def fetch_rss(query: str) -> list[dict]:
    """Unlimited fallback: search RSS feeds by keyword."""
    results: list[dict] = []
    keywords = query.lower().split()

    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:30]:
                title = entry.get("title", "")
                if not keywords or any(k in title.lower() for k in keywords):
                    results.append(
                        {
                            "title": title,
                            "source": feed.feed.get("title", feed_url),
                            "published": (entry.get("published", "") or "")[:10],
                            "url": entry.get("link", ""),
                            "description": entry.get("summary", "")[:200],
                        }
                    )
        except Exception:
            continue

    return results[:5]
