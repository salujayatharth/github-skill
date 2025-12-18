#!/usr/bin/env python3
"""
Issue management for GitHub.

Usage:
    python issues.py list --owner OWNER --repo REPO
    python issues.py get --owner OWNER --repo REPO --number NUM
    python issues.py create --owner OWNER --repo REPO --title TITLE
    python issues.py update --owner OWNER --repo REPO --number NUM
    python issues.py comment --owner OWNER --repo REPO --number NUM --body TEXT
    python issues.py list-comments --owner OWNER --repo REPO --number NUM
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from github_client import make_request
from utils import output_json, add_pagination_args, add_format_args, get_pagination_params


def list_issues(owner, repo, state="open", labels=None, assignee=None,
                creator=None, mentioned=None, sort="created", direction="desc",
                since=None, per_page=30, page=1):
    """List repository issues."""
    params = {
        "state": state,
        "sort": sort,
        "direction": direction,
        "per_page": per_page,
        "page": page
    }
    if labels:
        params["labels"] = labels
    if assignee:
        params["assignee"] = assignee
    if creator:
        params["creator"] = creator
    if mentioned:
        params["mentioned"] = mentioned
    if since:
        params["since"] = since

    return make_request(f"/repos/{owner}/{repo}/issues", params=params)


def get_issue(owner, repo, number):
    """Get single issue."""
    return make_request(f"/repos/{owner}/{repo}/issues/{number}")


def create_issue(owner, repo, title, body=None, labels=None, assignees=None, milestone=None):
    """Create new issue."""
    data = {"title": title}

    if body:
        data["body"] = body
    if labels:
        data["labels"] = labels.split(",") if isinstance(labels, str) else labels
    if assignees:
        data["assignees"] = assignees.split(",") if isinstance(assignees, str) else assignees
    if milestone:
        data["milestone"] = milestone

    return make_request(f"/repos/{owner}/{repo}/issues", method="POST", data=data)


def update_issue(owner, repo, number, title=None, body=None, state=None,
                state_reason=None, labels=None, assignees=None, milestone=None):
    """Update existing issue."""
    data = {}

    if title is not None:
        data["title"] = title
    if body is not None:
        data["body"] = body
    if state is not None:
        data["state"] = state
    if state_reason is not None:
        data["state_reason"] = state_reason
    if labels is not None:
        data["labels"] = labels.split(",") if isinstance(labels, str) else labels
    if assignees is not None:
        data["assignees"] = assignees.split(",") if isinstance(assignees, str) else assignees
    if milestone is not None:
        data["milestone"] = milestone

    return make_request(f"/repos/{owner}/{repo}/issues/{number}", method="PATCH", data=data)


def add_comment(owner, repo, number, body):
    """Add comment to issue."""
    return make_request(
        f"/repos/{owner}/{repo}/issues/{number}/comments",
        method="POST",
        data={"body": body}
    )


def list_comments(owner, repo, number, since=None, per_page=30, page=1):
    """List issue comments."""
    params = {"per_page": per_page, "page": page}
    if since:
        params["since"] = since

    return make_request(
        f"/repos/{owner}/{repo}/issues/{number}/comments",
        params=params
    )


def update_comment(owner, repo, comment_id, body):
    """Update existing comment."""
    return make_request(
        f"/repos/{owner}/{repo}/issues/comments/{comment_id}",
        method="PATCH",
        data={"body": body}
    )


def delete_comment(owner, repo, comment_id):
    """Delete comment."""
    make_request(
        f"/repos/{owner}/{repo}/issues/comments/{comment_id}",
        method="DELETE"
    )
    return {"deleted": True, "comment_id": comment_id}


def add_labels(owner, repo, number, labels):
    """Add labels to issue."""
    label_list = labels.split(",") if isinstance(labels, str) else labels
    return make_request(
        f"/repos/{owner}/{repo}/issues/{number}/labels",
        method="POST",
        data={"labels": label_list}
    )


def remove_label(owner, repo, number, label):
    """Remove label from issue."""
    make_request(
        f"/repos/{owner}/{repo}/issues/{number}/labels/{label}",
        method="DELETE"
    )
    return {"removed": True, "label": label}


def lock_issue(owner, repo, number, reason=None):
    """Lock issue conversation."""
    data = {}
    if reason:
        data["lock_reason"] = reason
    make_request(
        f"/repos/{owner}/{repo}/issues/{number}/lock",
        method="PUT",
        data=data if data else None
    )
    return {"locked": True, "issue_number": number}


def unlock_issue(owner, repo, number):
    """Unlock issue conversation."""
    make_request(
        f"/repos/{owner}/{repo}/issues/{number}/lock",
        method="DELETE"
    )
    return {"unlocked": True, "issue_number": number}


def main():
    parser = argparse.ArgumentParser(
        description="GitHub issue operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python issues.py list --owner octocat --repo Hello-World --state open
  python issues.py get --owner octocat --repo Hello-World --number 1
  python issues.py create --owner myuser --repo myrepo --title "Bug report" --body "Details here"
  python issues.py update --owner myuser --repo myrepo --number 1 --state closed
  python issues.py comment --owner myuser --repo myrepo --number 1 --body "Thanks for the report!"
        """
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list
    p = subparsers.add_parser("list", help="List issues")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--state", choices=["open", "closed", "all"], default="open",
                  help="Issue state filter")
    p.add_argument("--labels", help="Comma-separated label names")
    p.add_argument("--assignee", help="Filter by assignee username")
    p.add_argument("--creator", help="Filter by creator username")
    p.add_argument("--mentioned", help="Filter by mentioned username")
    p.add_argument("--sort", choices=["created", "updated", "comments"], default="created")
    p.add_argument("--direction", choices=["asc", "desc"], default="desc")
    p.add_argument("--since", help="Only issues updated after this time (ISO 8601)")
    add_pagination_args(p)
    add_format_args(p)

    # get
    p = subparsers.add_parser("get", help="Get single issue")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--number", type=int, required=True, help="Issue number")
    add_format_args(p)

    # create
    p = subparsers.add_parser("create", help="Create new issue")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--title", required=True, help="Issue title")
    p.add_argument("--body", help="Issue body/description")
    p.add_argument("--labels", help="Comma-separated label names")
    p.add_argument("--assignees", help="Comma-separated usernames to assign")
    p.add_argument("--milestone", type=int, help="Milestone number")
    add_format_args(p)

    # update
    p = subparsers.add_parser("update", help="Update existing issue")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--number", type=int, required=True, help="Issue number")
    p.add_argument("--title", help="New title")
    p.add_argument("--body", help="New body")
    p.add_argument("--state", choices=["open", "closed"], help="New state")
    p.add_argument("--state-reason", choices=["completed", "not_planned", "reopened"],
                  help="Reason for state change")
    p.add_argument("--labels", help="Comma-separated labels (replaces existing)")
    p.add_argument("--assignees", help="Comma-separated assignees (replaces existing)")
    p.add_argument("--milestone", type=int, help="Milestone number")
    add_format_args(p)

    # comment
    p = subparsers.add_parser("comment", help="Add comment to issue")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--number", type=int, required=True, help="Issue number")
    p.add_argument("--body", required=True, help="Comment text")
    add_format_args(p)

    # list-comments
    p = subparsers.add_parser("list-comments", help="List issue comments")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--number", type=int, required=True, help="Issue number")
    p.add_argument("--since", help="Only comments after this time (ISO 8601)")
    add_pagination_args(p)
    add_format_args(p)

    # update-comment
    p = subparsers.add_parser("update-comment", help="Update existing comment")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--comment-id", type=int, required=True, help="Comment ID")
    p.add_argument("--body", required=True, help="New comment text")
    add_format_args(p)

    # delete-comment
    p = subparsers.add_parser("delete-comment", help="Delete comment")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--comment-id", type=int, required=True, help="Comment ID")
    add_format_args(p)

    # add-labels
    p = subparsers.add_parser("add-labels", help="Add labels to issue")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--number", type=int, required=True, help="Issue number")
    p.add_argument("--labels", required=True, help="Comma-separated labels to add")
    add_format_args(p)

    # remove-label
    p = subparsers.add_parser("remove-label", help="Remove label from issue")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--number", type=int, required=True, help="Issue number")
    p.add_argument("--label", required=True, help="Label name to remove")
    add_format_args(p)

    # lock
    p = subparsers.add_parser("lock", help="Lock issue conversation")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--number", type=int, required=True, help="Issue number")
    p.add_argument("--reason", choices=["off-topic", "too heated", "resolved", "spam"],
                  help="Lock reason")
    add_format_args(p)

    # unlock
    p = subparsers.add_parser("unlock", help="Unlock issue conversation")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--number", type=int, required=True, help="Issue number")
    add_format_args(p)

    args = parser.parse_args()

    # Execute command
    if args.command == "list":
        result = list_issues(args.owner, args.repo, args.state, args.labels,
                            args.assignee, args.creator, args.mentioned,
                            args.sort, args.direction, args.since,
                            args.per_page, args.page)
    elif args.command == "get":
        result = get_issue(args.owner, args.repo, args.number)
    elif args.command == "create":
        result = create_issue(args.owner, args.repo, args.title, args.body,
                             args.labels, args.assignees, args.milestone)
    elif args.command == "update":
        result = update_issue(args.owner, args.repo, args.number, args.title,
                             args.body, args.state, args.state_reason,
                             args.labels, args.assignees, args.milestone)
    elif args.command == "comment":
        result = add_comment(args.owner, args.repo, args.number, args.body)
    elif args.command == "list-comments":
        result = list_comments(args.owner, args.repo, args.number,
                              args.since, args.per_page, args.page)
    elif args.command == "update-comment":
        result = update_comment(args.owner, args.repo, args.comment_id, args.body)
    elif args.command == "delete-comment":
        result = delete_comment(args.owner, args.repo, args.comment_id)
    elif args.command == "add-labels":
        result = add_labels(args.owner, args.repo, args.number, args.labels)
    elif args.command == "remove-label":
        result = remove_label(args.owner, args.repo, args.number, args.label)
    elif args.command == "lock":
        result = lock_issue(args.owner, args.repo, args.number, args.reason)
    elif args.command == "unlock":
        result = unlock_issue(args.owner, args.repo, args.number)

    output_json(result, args.format)


if __name__ == "__main__":
    main()
