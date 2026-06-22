from agents.base import BaseAgent
from tools.github_api import (
    get_open_prs,
    get_assigned_issues,
    get_recent_commits,
    get_github_summary,
)


class GithubAgent(BaseAgent):
    name = "github"
    description = (
        "Checks GitHub activity: open PRs awaiting review, assigned issues, "
        "and recent commits. Use for questions about code review, GitHub tasks, "
        "or repository activity."
    )

    def run(self, query: str) -> str:
        q = query.lower()

        if any(w in q for w in ("pr", "pull request", "review")):
            return get_open_prs()
        if any(w in q for w in ("issue", "bug", "task")):
            return get_assigned_issues()
        if any(w in q for w in ("commit", "push", "merged", "deploy")):
            return get_recent_commits()

        return get_github_summary()
