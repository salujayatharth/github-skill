#!/usr/bin/env python3
"""
Pull request operations for GitHub.

Usage:
    python pull_requests.py list --owner OWNER --repo REPO
    python pull_requests.py get --owner OWNER --repo REPO --number NUM
    python pull_requests.py create --owner OWNER --repo REPO --title TITLE --head BRANCH --base BRANCH
    python pull_requests.py files --owner OWNER --repo REPO --number NUM
    python pull_requests.py merge --owner OWNER --repo REPO --number NUM
    python pull_requests.py reviews --owner OWNER --repo REPO --number NUM
    python pull_requests.py review --owner OWNER --repo REPO --number NUM --event APPROVE|REQUEST_CHANGES|COMMENT
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from github_client import make_request
from utils import output_json, add_pagination_args, add_format_args


def list_prs(owner, repo, state="open", head=None, base=None, sort="created",
             direction="desc", per_page=30, page=1):
    """List pull requests."""
    params = {
        "state": state,
        "sort": sort,
        "direction": direction,
        "per_page": per_page,
        "page": page
    }
    if head:
        params["head"] = head
    if base:
        params["base"] = base

    return make_request(f"/repos/{owner}/{repo}/pulls", params=params)


def get_pr(owner, repo, number):
    """Get single pull request."""
    return make_request(f"/repos/{owner}/{repo}/pulls/{number}")


def create_pr(owner, repo, title, head, base, body=None, draft=False,
              maintainer_can_modify=True):
    """Create pull request."""
    data = {
        "title": title,
        "head": head,
        "base": base,
        "draft": draft,
        "maintainer_can_modify": maintainer_can_modify
    }
    if body:
        data["body"] = body

    return make_request(f"/repos/{owner}/{repo}/pulls", method="POST", data=data)


def update_pr(owner, repo, number, title=None, body=None, state=None, base=None,
              maintainer_can_modify=None):
    """Update pull request."""
    data = {}
    if title is not None:
        data["title"] = title
    if body is not None:
        data["body"] = body
    if state is not None:
        data["state"] = state
    if base is not None:
        data["base"] = base
    if maintainer_can_modify is not None:
        data["maintainer_can_modify"] = maintainer_can_modify

    return make_request(f"/repos/{owner}/{repo}/pulls/{number}", method="PATCH", data=data)


def get_files(owner, repo, number, per_page=30, page=1):
    """List files changed in PR."""
    return make_request(
        f"/repos/{owner}/{repo}/pulls/{number}/files",
        params={"per_page": per_page, "page": page}
    )


def get_commits(owner, repo, number, per_page=30, page=1):
    """List commits in PR."""
    return make_request(
        f"/repos/{owner}/{repo}/pulls/{number}/commits",
        params={"per_page": per_page, "page": page}
    )


def merge_pr(owner, repo, number, commit_title=None, commit_message=None,
             merge_method="merge", sha=None):
    """Merge pull request."""
    data = {"merge_method": merge_method}
    if commit_title:
        data["commit_title"] = commit_title
    if commit_message:
        data["commit_message"] = commit_message
    if sha:
        data["sha"] = sha

    return make_request(
        f"/repos/{owner}/{repo}/pulls/{number}/merge",
        method="PUT",
        data=data
    )


def check_mergeable(owner, repo, number):
    """Check if PR is mergeable."""
    pr = make_request(f"/repos/{owner}/{repo}/pulls/{number}")
    return {
        "number": number,
        "mergeable": pr.get("mergeable"),
        "mergeable_state": pr.get("mergeable_state"),
        "rebaseable": pr.get("rebaseable"),
        "merge_commit_sha": pr.get("merge_commit_sha")
    }


def update_branch(owner, repo, number, expected_head_sha=None):
    """Update PR branch with latest from base."""
    data = {}
    if expected_head_sha:
        data["expected_head_sha"] = expected_head_sha

    return make_request(
        f"/repos/{owner}/{repo}/pulls/{number}/update-branch",
        method="PUT",
        data=data if data else None
    )


def list_reviews(owner, repo, number, per_page=30, page=1):
    """List reviews on PR."""
    return make_request(
        f"/repos/{owner}/{repo}/pulls/{number}/reviews",
        params={"per_page": per_page, "page": page}
    )


def create_review(owner, repo, number, event, body=None, comments=None, commit_id=None):
    """Create PR review.

    Args:
        event: APPROVE, REQUEST_CHANGES, or COMMENT
        body: Review body text
        comments: List of review comments (for line-by-line feedback)
        commit_id: SHA of commit to review
    """
    data = {"event": event}
    if body:
        data["body"] = body
    if comments:
        data["comments"] = comments
    if commit_id:
        data["commit_id"] = commit_id

    return make_request(
        f"/repos/{owner}/{repo}/pulls/{number}/reviews",
        method="POST",
        data=data
    )


def dismiss_review(owner, repo, number, review_id, message):
    """Dismiss a review."""
    return make_request(
        f"/repos/{owner}/{repo}/pulls/{number}/reviews/{review_id}/dismissals",
        method="PUT",
        data={"message": message}
    )


def request_reviewers(owner, repo, number, reviewers=None, team_reviewers=None):
    """Request reviewers for PR."""
    data = {}
    if reviewers:
        data["reviewers"] = reviewers.split(",") if isinstance(reviewers, str) else reviewers
    if team_reviewers:
        data["team_reviewers"] = team_reviewers.split(",") if isinstance(team_reviewers, str) else team_reviewers

    return make_request(
        f"/repos/{owner}/{repo}/pulls/{number}/requested_reviewers",
        method="POST",
        data=data
    )


def remove_reviewers(owner, repo, number, reviewers=None, team_reviewers=None):
    """Remove requested reviewers from PR."""
    data = {}
    if reviewers:
        data["reviewers"] = reviewers.split(",") if isinstance(reviewers, str) else reviewers
    if team_reviewers:
        data["team_reviewers"] = team_reviewers.split(",") if isinstance(team_reviewers, str) else team_reviewers

    return make_request(
        f"/repos/{owner}/{repo}/pulls/{number}/requested_reviewers",
        method="DELETE",
        data=data
    )


def get_status(owner, repo, number):
    """Get combined status of all checks for PR's head commit."""
    pr = make_request(f"/repos/{owner}/{repo}/pulls/{number}")
    head_sha = pr["head"]["sha"]

    # Get combined status
    status = make_request(f"/repos/{owner}/{repo}/commits/{head_sha}/status")

    # Get check runs
    checks = make_request(f"/repos/{owner}/{repo}/commits/{head_sha}/check-runs")

    return {
        "sha": head_sha,
        "state": status.get("state"),
        "total_count": status.get("total_count", 0),
        "statuses": status.get("statuses", []),
        "check_runs": checks.get("check_runs", [])
    }


def add_comment(owner, repo, number, body):
    """Add comment to PR (same as issue comment)."""
    return make_request(
        f"/repos/{owner}/{repo}/issues/{number}/comments",
        method="POST",
        data={"body": body}
    )


def list_comments(owner, repo, number, per_page=30, page=1):
    """List PR comments (both issue comments and review comments)."""
    # Issue comments
    issue_comments = make_request(
        f"/repos/{owner}/{repo}/issues/{number}/comments",
        params={"per_page": per_page, "page": page}
    )

    return issue_comments


def main():
    parser = argparse.ArgumentParser(
        description="GitHub pull request operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pull_requests.py list --owner octocat --repo Hello-World
  python pull_requests.py get --owner octocat --repo Hello-World --number 1
  python pull_requests.py create --owner myuser --repo myrepo --title "New feature" --head feature-branch --base main
  python pull_requests.py merge --owner myuser --repo myrepo --number 1 --method squash
  python pull_requests.py review --owner myuser --repo myrepo --number 1 --event APPROVE --body "LGTM!"
        """
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list
    p = subparsers.add_parser("list", help="List pull requests")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--state", choices=["open", "closed", "all"], default="open")
    p.add_argument("--head", help="Filter by head branch (user:branch or branch)")
    p.add_argument("--base", help="Filter by base branch")
    p.add_argument("--sort", choices=["created", "updated", "popularity", "long-running"],
                  default="created")
    p.add_argument("--direction", choices=["asc", "desc"], default="desc")
    add_pagination_args(p)
    add_format_args(p)

    # get
    p = subparsers.add_parser("get", help="Get pull request details")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--number", type=int, required=True, help="PR number")
    add_format_args(p)

    # create
    p = subparsers.add_parser("create", help="Create pull request")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--title", required=True, help="PR title")
    p.add_argument("--head", required=True, help="Head branch (source)")
    p.add_argument("--base", required=True, help="Base branch (target)")
    p.add_argument("--body", help="PR description")
    p.add_argument("--draft", action="store_true", help="Create as draft PR")
    add_format_args(p)

    # update
    p = subparsers.add_parser("update", help="Update pull request")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--number", type=int, required=True, help="PR number")
    p.add_argument("--title", help="New title")
    p.add_argument("--body", help="New description")
    p.add_argument("--state", choices=["open", "closed"], help="New state")
    p.add_argument("--base", help="New base branch")
    add_format_args(p)

    # files
    p = subparsers.add_parser("files", help="List files changed in PR")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--number", type=int, required=True, help="PR number")
    add_pagination_args(p)
    add_format_args(p)

    # commits
    p = subparsers.add_parser("commits", help="List commits in PR")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--number", type=int, required=True, help="PR number")
    add_pagination_args(p)
    add_format_args(p)

    # merge
    p = subparsers.add_parser("merge", help="Merge pull request")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--number", type=int, required=True, help="PR number")
    p.add_argument("--method", choices=["merge", "squash", "rebase"], default="merge",
                  help="Merge method")
    p.add_argument("--commit-title", help="Custom merge commit title")
    p.add_argument("--commit-message", help="Custom merge commit message")
    p.add_argument("--sha", help="Expected head SHA (safety check)")
    add_format_args(p)

    # check-mergeable
    p = subparsers.add_parser("check-mergeable", help="Check if PR is mergeable")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--number", type=int, required=True, help="PR number")
    add_format_args(p)

    # update-branch
    p = subparsers.add_parser("update-branch", help="Update PR branch with base")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--number", type=int, required=True, help="PR number")
    p.add_argument("--expected-sha", help="Expected head SHA (safety check)")
    add_format_args(p)

    # reviews
    p = subparsers.add_parser("reviews", help="List PR reviews")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--number", type=int, required=True, help="PR number")
    add_pagination_args(p)
    add_format_args(p)

    # review
    p = subparsers.add_parser("review", help="Create PR review")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--number", type=int, required=True, help="PR number")
    p.add_argument("--event", required=True, choices=["APPROVE", "REQUEST_CHANGES", "COMMENT"],
                  help="Review decision")
    p.add_argument("--body", help="Review comment")
    add_format_args(p)

    # dismiss-review
    p = subparsers.add_parser("dismiss-review", help="Dismiss a review")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--number", type=int, required=True, help="PR number")
    p.add_argument("--review-id", type=int, required=True, help="Review ID")
    p.add_argument("--message", required=True, help="Dismissal reason")
    add_format_args(p)

    # request-reviewers
    p = subparsers.add_parser("request-reviewers", help="Request reviewers")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--number", type=int, required=True, help="PR number")
    p.add_argument("--reviewers", help="Comma-separated usernames")
    p.add_argument("--team-reviewers", help="Comma-separated team slugs")
    add_format_args(p)

    # remove-reviewers
    p = subparsers.add_parser("remove-reviewers", help="Remove requested reviewers")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--number", type=int, required=True, help="PR number")
    p.add_argument("--reviewers", help="Comma-separated usernames")
    p.add_argument("--team-reviewers", help="Comma-separated team slugs")
    add_format_args(p)

    # status
    p = subparsers.add_parser("status", help="Get CI/check status for PR")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--number", type=int, required=True, help="PR number")
    add_format_args(p)

    # comment
    p = subparsers.add_parser("comment", help="Add comment to PR")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--number", type=int, required=True, help="PR number")
    p.add_argument("--body", required=True, help="Comment text")
    add_format_args(p)

    # list-comments
    p = subparsers.add_parser("list-comments", help="List PR comments")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--number", type=int, required=True, help="PR number")
    add_pagination_args(p)
    add_format_args(p)

    args = parser.parse_args()

    # Execute command
    if args.command == "list":
        result = list_prs(args.owner, args.repo, args.state, args.head, args.base,
                         args.sort, args.direction, args.per_page, args.page)
    elif args.command == "get":
        result = get_pr(args.owner, args.repo, args.number)
    elif args.command == "create":
        result = create_pr(args.owner, args.repo, args.title, args.head, args.base,
                          args.body, args.draft)
    elif args.command == "update":
        result = update_pr(args.owner, args.repo, args.number, args.title,
                          args.body, args.state, args.base)
    elif args.command == "files":
        result = get_files(args.owner, args.repo, args.number, args.per_page, args.page)
    elif args.command == "commits":
        result = get_commits(args.owner, args.repo, args.number, args.per_page, args.page)
    elif args.command == "merge":
        result = merge_pr(args.owner, args.repo, args.number, args.commit_title,
                         args.commit_message, args.method, args.sha)
    elif args.command == "check-mergeable":
        result = check_mergeable(args.owner, args.repo, args.number)
    elif args.command == "update-branch":
        result = update_branch(args.owner, args.repo, args.number, args.expected_sha)
    elif args.command == "reviews":
        result = list_reviews(args.owner, args.repo, args.number, args.per_page, args.page)
    elif args.command == "review":
        result = create_review(args.owner, args.repo, args.number, args.event, args.body)
    elif args.command == "dismiss-review":
        result = dismiss_review(args.owner, args.repo, args.number, args.review_id, args.message)
    elif args.command == "request-reviewers":
        result = request_reviewers(args.owner, args.repo, args.number,
                                  args.reviewers, args.team_reviewers)
    elif args.command == "remove-reviewers":
        result = remove_reviewers(args.owner, args.repo, args.number,
                                 args.reviewers, args.team_reviewers)
    elif args.command == "status":
        result = get_status(args.owner, args.repo, args.number)
    elif args.command == "comment":
        result = add_comment(args.owner, args.repo, args.number, args.body)
    elif args.command == "list-comments":
        result = list_comments(args.owner, args.repo, args.number, args.per_page, args.page)

    output_json(result, args.format)


if __name__ == "__main__":
    main()
