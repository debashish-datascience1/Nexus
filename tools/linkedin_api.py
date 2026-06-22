from config import LINKEDIN_EMAIL, LINKEDIN_PASSWORD

_NO_CREDS = (
    "LinkedIn credentials not configured. "
    "Add LINKEDIN_EMAIL and LINKEDIN_PASSWORD to your .env file."
)


def _client():
    from linkedin_api import Linkedin
    return Linkedin(LINKEDIN_EMAIL, LINKEDIN_PASSWORD)


def get_connection_requests() -> str:
    if not LINKEDIN_EMAIL or not LINKEDIN_PASSWORD:
        return _NO_CREDS
    try:
        api = _client()
        invitations = api.get_invitations(start=0, limit=10)
        if not invitations:
            return "No pending connection requests."
        lines = []
        for inv in invitations:
            from_member = inv.get("fromMember", {})
            name = f"{from_member.get('firstName', '')} {from_member.get('lastName', '')}".strip()
            headline = from_member.get("headline", "")
            lines.append(f"• {name or 'Unknown'}" + (f"  —  {headline}" if headline else ""))
        return "\n".join(lines)
    except Exception as e:
        return f"LinkedIn error: {e}"


def get_notifications() -> str:
    if not LINKEDIN_EMAIL or not LINKEDIN_PASSWORD:
        return _NO_CREDS
    try:
        api = _client()
        notifs = api.get_user_profile()
        first = notifs.get("firstName", {}).get("localized", {})
        last  = notifs.get("lastName", {}).get("localized", {})
        name  = f"{list(first.values())[0] if first else ''} {list(last.values())[0] if last else ''}".strip()
        return f"Logged in as: {name}\n\nUse specific queries like 'connection requests' for more detail."
    except Exception as e:
        return f"LinkedIn error: {e}"


def get_feed_posts(limit: int = 5) -> str:
    if not LINKEDIN_EMAIL or not LINKEDIN_PASSWORD:
        return _NO_CREDS
    try:
        api = _client()
        feed = api.get_feed_posts(limit=limit)
        if not feed:
            return "No recent feed posts found."
        lines = []
        for post in feed[:limit]:
            actor = post.get("actor", {}).get("name", {}).get("text", "Unknown")
            text  = post.get("commentary", {}).get("text", {}).get("text", "")[:150]
            lines.append(f"• **{actor}**: {text}")
        return "\n\n".join(lines)
    except Exception as e:
        return f"LinkedIn error: {e}"
