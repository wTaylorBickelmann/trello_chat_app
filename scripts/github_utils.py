"""Utilities for interacting with the GitHub API via PyGithub.

The following env vars must be provided:
- GH_PAT: Personal Access Token (repo scope)

"""
from __future__ import annotations

import os
from datetime import datetime
from typing import List, Tuple

from github import Github, Issue

REPO_NAME = "wTaylorBickelmann/trello_chat_app"
INPUT_LABEL = "daily-input"


def _client() -> Github:
    return Github(os.environ["GH_PAT"])


def get_repo():
    return _client().get_repo(REPO_NAME)


def get_open_daily_inputs() -> List[Issue.Issue]:
    """Return all open issues labeled daily-input."""
    repo = get_repo()
    return list(repo.get_issues(state="open", labels=[INPUT_LABEL]))


def comment_and_close(issue: Issue.Issue, body: str) -> None:
    issue.create_comment(body)
    issue.edit(state="closed")


def archive_inputs(issues: List[Issue.Issue], save_dir: str = "inputs") -> None:
    """Save each issue body as a timestamped markdown file for RAG."""
    os.makedirs(save_dir, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    for idx, issue in enumerate(issues):
        filename = f"{save_dir}/{ts}_{idx}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(issue.body)
