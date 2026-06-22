from agents.base import BaseAgent
from tools.linkedin_api import get_connection_requests, get_notifications, get_feed_posts


class LinkedinAgent(BaseAgent):
    name = "linkedin"
    description = (
        "Reads LinkedIn data: pending connection requests, feed posts, and profile info. "
        "Use for questions about LinkedIn activity, connections, or your feed."
    )

    def run(self, query: str) -> str:
        q = query.lower()

        if any(w in q for w in ("connect", "invitation", "request", "pending")):
            return get_connection_requests()
        if any(w in q for w in ("feed", "post", "update", "latest")):
            return get_feed_posts()

        return get_notifications()
