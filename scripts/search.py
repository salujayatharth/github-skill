#!/usr/bin/env python3
"""
GitHub search operations.

Usage:
    python search.py repos --query "QUERY"
    python search.py code --query "QUERY"
    python search.py issues --query "QUERY"
    python search.py users --query "QUERY"
    python search.py commits --query "QUERY"
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from github_client import make_request
from utils import output_json, add_pagination_args, add_format_args


def search_repos(query, sort=None, order="desc", per_page=30, page=1):
    """Search repositories.

    Query syntax examples:
    - language:python stars:>1000
    - user:octocat
    - org:github
    - topic:machine-learning
    """
    params = {
        "q": query,
        "order": order,
        "per_page": per_page,
        "page": page
    }
    if sort:
        params["sort"] = sort

    return make_request("/search/repositories", params=params)


def search_code(query, sort=None, order="desc", per_page=30, page=1):
    """Search code.

    Query syntax examples:
    - addClass in:file language:javascript
    - repo:owner/repo path:src extension:py
    - filename:config.yml
    - org:github extension:rb

    Note: Code search requires authentication.
    """
    params = {
        "q": query,
        "order": order,
        "per_page": per_page,
        "page": page
    }
    if sort:
        params["sort"] = sort

    return make_request("/search/code", params=params)


def search_issues(query, sort=None, order="desc", per_page=30, page=1):
    """Search issues and pull requests.

    Query syntax examples:
    - repo:owner/repo is:open is:issue label:bug
    - author:username is:pr is:merged
    - mentions:username
    - assignee:username is:open
    - org:github type:pr is:open
    """
    params = {
        "q": query,
        "order": order,
        "per_page": per_page,
        "page": page
    }
    if sort:
        params["sort"] = sort

    return make_request("/search/issues", params=params)


def search_users(query, sort=None, order="desc", per_page=30, page=1):
    """Search users.

    Query syntax examples:
    - fullname:John location:USA
    - type:user followers:>1000
    - language:python
    - type:org
    """
    params = {
        "q": query,
        "order": order,
        "per_page": per_page,
        "page": page
    }
    if sort:
        params["sort"] = sort

    return make_request("/search/users", params=params)


def search_commits(query, sort=None, order="desc", per_page=30, page=1):
    """Search commits.

    Query syntax examples:
    - repo:owner/repo fix bug
    - author:username committer-date:>2024-01-01
    - org:github merge
    """
    params = {
        "q": query,
        "order": order,
        "per_page": per_page,
        "page": page
    }
    if sort:
        params["sort"] = sort

    return make_request(
        "/search/commits",
        params=params,
        accept="application/vnd.github.cloak-preview+json"
    )


def search_topics(query, per_page=30, page=1):
    """Search topics.

    Query syntax examples:
    - machine-learning
    - javascript
    """
    params = {
        "q": query,
        "per_page": per_page,
        "page": page
    }

    return make_request(
        "/search/topics",
        params=params,
        accept="application/vnd.github.mercy-preview+json"
    )


def search_labels(owner, repo, query, per_page=30, page=1):
    """Search labels in a repository."""
    params = {
        "q": query,
        "per_page": per_page,
        "page": page
    }

    return make_request(
        f"/search/labels",
        params={"repository_id": f"{owner}/{repo}", **params}
    )


def main():
    parser = argparse.ArgumentParser(
        description="GitHub search operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python search.py repos --query "language:python stars:>1000"
  python search.py code --query "def main repo:owner/repo extension:py"
  python search.py issues --query "repo:owner/repo is:open label:bug"
  python search.py users --query "location:SF followers:>100"
  python search.py commits --query "repo:owner/repo fix"

Query Syntax Help:
  Repositories:
    language:python     - Filter by language
    stars:>1000        - Filter by stars
    user:octocat       - Filter by user
    org:github         - Filter by organization
    topic:ml           - Filter by topic
    fork:true          - Include forks

  Code:
    in:file            - Search in file contents
    in:path            - Search in file paths
    extension:py       - Filter by file extension
    filename:config    - Search by filename
    path:src/          - Search in path
    repo:owner/repo    - Search in specific repo

  Issues/PRs:
    is:open/closed     - Filter by state
    is:issue/pr        - Filter by type
    is:merged          - Merged PRs only
    label:bug          - Filter by label
    author:user        - Filter by author
    assignee:user      - Filter by assignee
    mentions:user      - Filter by mentions

  Users:
    type:user/org      - Filter by type
    followers:>100     - Filter by followers
    location:SF        - Filter by location
    language:python    - Filter by language

  Commits:
    author:user        - Filter by author
    committer:user     - Filter by committer
    author-date:>DATE  - Filter by author date
    committer-date:>DATE - Filter by commit date
        """
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # repos
    p = subparsers.add_parser("repos", help="Search repositories")
    p.add_argument("--query", "-q", required=True, help="Search query")
    p.add_argument("--sort", choices=["stars", "forks", "help-wanted-issues", "updated"],
                  help="Sort field")
    p.add_argument("--order", choices=["asc", "desc"], default="desc", help="Sort order")
    add_pagination_args(p)
    add_format_args(p)

    # code
    p = subparsers.add_parser("code", help="Search code")
    p.add_argument("--query", "-q", required=True, help="Search query")
    p.add_argument("--sort", choices=["indexed"], help="Sort by indexed date")
    p.add_argument("--order", choices=["asc", "desc"], default="desc", help="Sort order")
    add_pagination_args(p)
    add_format_args(p)

    # issues
    p = subparsers.add_parser("issues", help="Search issues and PRs")
    p.add_argument("--query", "-q", required=True, help="Search query")
    p.add_argument("--sort", choices=["comments", "reactions", "reactions-+1",
                                       "reactions--1", "reactions-smile",
                                       "reactions-thinking_face", "reactions-heart",
                                       "reactions-tada", "interactions", "created", "updated"],
                  help="Sort field")
    p.add_argument("--order", choices=["asc", "desc"], default="desc", help="Sort order")
    add_pagination_args(p)
    add_format_args(p)

    # users
    p = subparsers.add_parser("users", help="Search users")
    p.add_argument("--query", "-q", required=True, help="Search query")
    p.add_argument("--sort", choices=["followers", "repositories", "joined"],
                  help="Sort field")
    p.add_argument("--order", choices=["asc", "desc"], default="desc", help="Sort order")
    add_pagination_args(p)
    add_format_args(p)

    # commits
    p = subparsers.add_parser("commits", help="Search commits")
    p.add_argument("--query", "-q", required=True, help="Search query")
    p.add_argument("--sort", choices=["author-date", "committer-date"],
                  help="Sort field")
    p.add_argument("--order", choices=["asc", "desc"], default="desc", help="Sort order")
    add_pagination_args(p)
    add_format_args(p)

    # topics
    p = subparsers.add_parser("topics", help="Search topics")
    p.add_argument("--query", "-q", required=True, help="Search query")
    add_pagination_args(p)
    add_format_args(p)

    args = parser.parse_args()

    # Execute command
    if args.command == "repos":
        result = search_repos(args.query, args.sort, args.order, args.per_page, args.page)
    elif args.command == "code":
        result = search_code(args.query, args.sort, args.order, args.per_page, args.page)
    elif args.command == "issues":
        result = search_issues(args.query, args.sort, args.order, args.per_page, args.page)
    elif args.command == "users":
        result = search_users(args.query, args.sort, args.order, args.per_page, args.page)
    elif args.command == "commits":
        result = search_commits(args.query, args.sort, args.order, args.per_page, args.page)
    elif args.command == "topics":
        result = search_topics(args.query, args.per_page, args.page)

    output_json(result, args.format)


if __name__ == "__main__":
    main()
