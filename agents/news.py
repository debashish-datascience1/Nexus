from agents.base import BaseAgent
from tools.newsapi import fetch_news, fetch_rss


class NewsAgent(BaseAgent):
    name = "news"
    description = (
        "Fetches top news headlines and articles. Use for questions like "
        "'what's happening in AI today', 'latest tech news', or any news topic."
    )

    def run(self, query: str) -> str:
        articles = fetch_news(query) or fetch_rss(query)

        if not articles:
            return "No articles found for that query. Try a broader search term."

        lines = []
        for a in articles:
            line = f"**{a['title']}**"
            if a["source"]:
                line += f"  —  {a['source']}"
            if a["published"]:
                line += f" ({a['published']})"
            if a["url"]:
                line += f"\n{a['url']}"
            lines.append(line)

        return "\n\n".join(lines)
