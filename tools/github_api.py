from github import Github, GithubException
from config import GITHUB_TOKEN

_NO_TOKEN = "GitHub token not configured. Add GITHUB_TOKEN to your .env file."


def _client() -> Github:
    return Github(GITHUB_TOKEN)


def get_open_prs() -> str:
    if not GITHUB_TOKEN:
        return _NO_TOKEN
    try:
        g = _client()
        user = g.get_user()
        results = g.search_issues(
            f"is:pr is:open review-requested:{user.login}"
        )
        prs = list(results[:5])
        if not prs:
            return "No open PRs are waiting for your review."
        lines = [
            f"• [{pr.title}]({pr.html_url})  —  {pr.repository.full_name}"
            for pr in prs
        ]
        return "\n".join(lines)
    except GithubException as e:
        return f"GitHub error: {e.data.get('message', str(e))}"


def get_assigned_issues() -> str:
    if not GITHUB_TOKEN:
        return _NO_TOKEN
    try:
        g = _client()
        user = g.get_user()
        results = g.search_issues(
            f"is:issue is:open assignee:{user.login}"
        )
        issues = list(results[:5])
        if not issues:
            return "No open issues assigned to you."
        lines = [
            f"• [{i.title}]({i.html_url})  —  {i.repository.full_name}"
            for i in issues
        ]
        return "\n".join(lines)
    except GithubException as e:
        return f"GitHub error: {e.data.get('message', str(e))}"


def get_recent_commits() -> str:
    if not GITHUB_TOKEN:
        return _NO_TOKEN
    try:
        g = _client()
        user = g.get_user()
        events = [e for e in user.get_events() if e.type == "PushEvent"][:5]
        if not events:
            return "No recent push events found."
        lines = []
        for ev in events:
            repo = ev.repo.name
            for commit in (ev.payload.get("commits") or [])[:2]:
                msg = commit.get("message", "").split("\n")[0][:70]
                lines.append(f"• `{repo}` — {msg}")
        return "\n".join(lines) if lines else "No recent commits found."
    except GithubException as e:
        return f"GitHub error: {e.data.get('message', str(e))}"


def get_github_summary() -> str:
    prs    = get_open_prs()
    issues = get_assigned_issues()
    return f"**PRs awaiting review:**\n{prs}\n\n**Assigned issues:**\n{issues}"
