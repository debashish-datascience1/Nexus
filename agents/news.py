import json
from agents.base import BaseAgent
from tools.newsapi import fetch_news, fetch_rss


class NewsAgent(BaseAgent):
    name = "news"
    description = (
        "Fetches top news headlines and articles for any topic. Use for questions like "
        "'what's happening in AI today', 'latest cricket news', 'Virat Kohli updates', "
        "'news in India', 'politics', or any news subject."
    )

    def run(self, query: str) -> str:
        articles = fetch_news(query) or fetch_rss(query)
        if not articles:
            return json.dumps([])
        return json.dumps(articles)
