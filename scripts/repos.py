#!/usr/bin/env python3
"""
Repository operations for GitHub.

Usage:
    python repos.py get-file --owner OWNER --repo REPO --path PATH
    python repos.py list-files --owner OWNER --repo REPO [--path PATH]
    python repos.py create-file --owner OWNER --repo REPO --path PATH --content CONTENT --message MSG
    python repos.py push-files --owner OWNER --repo REPO --branch BRANCH --message MSG --files JSON
    python repos.py create-branch --owner OWNER --repo REPO --branch NAME
    python repos.py create-repo --name NAME [--description DESC] [--private]
    python repos.py fork --owner OWNER --repo REPO
    python repos.py get --owner OWNER --repo REPO
    python repos.py list-branches --owner OWNER --repo REPO
"""

import argparse
import base64
import json
import sys
import os

# Add scripts directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from github_client import make_request
from utils import output_json, add_pagination_args, add_format_args, get_pagination_params, error


def get_file(owner, repo, path, branch=None):
    """Get file or directory contents."""
    endpoint = f"/repos/{owner}/{repo}/contents/{path}"
    params = {"ref": branch} if branch else {}
    result = make_request(endpoint, params=params)

    # Decode file content if it's a file (not a directory)
    if isinstance(result, dict) and result.get("type") == "file" and result.get("content"):
        try:
            result["decoded_content"] = base64.b64decode(result["content"]).decode("utf-8")
        except (UnicodeDecodeError, ValueError):
            result["decoded_content"] = "[Binary file - cannot decode as text]"

    return result


def list_files(owner, repo, path="", branch=None):
    """List files in directory."""
    return get_file(owner, repo, path, branch)


def create_file(owner, repo, path, content, message, branch=None, sha=None):
    """Create or update a file.

    Args:
        owner: Repository owner
        repo: Repository name
        path: File path within repository
        content: File content as string
        message: Commit message
        branch: Branch name (optional, defaults to default branch)
        sha: Current file SHA (required for updates)
    """
    endpoint = f"/repos/{owner}/{repo}/contents/{path}"
    data = {
        "message": message,
        "content": base64.b64encode(content.encode("utf-8")).decode("ascii")
    }
    if branch:
        data["branch"] = branch
    if sha:
        data["sha"] = sha

    return make_request(endpoint, method="PUT", data=data)


def push_files(owner, repo, branch, message, files):
    """Push multiple files in single commit using Git Data API.

    Args:
        owner: Repository owner
        repo: Repository name
        branch: Target branch
        message: Commit message
        files: Dict of {path: content} pairs
    """
    # Get current commit SHA for branch
    ref = make_request(f"/repos/{owner}/{repo}/git/ref/heads/{branch}")
    current_sha = ref["object"]["sha"]

    # Get current tree
    commit = make_request(f"/repos/{owner}/{repo}/git/commits/{current_sha}")
    base_tree = commit["tree"]["sha"]

    # Create blobs for each file
    tree_items = []
    for path, content in files.items():
        blob = make_request(
            f"/repos/{owner}/{repo}/git/blobs",
            method="POST",
            data={"content": content, "encoding": "utf-8"}
        )
        tree_items.append({
            "path": path,
            "mode": "100644",
            "type": "blob",
            "sha": blob["sha"]
        })

    # Create new tree
    tree = make_request(
        f"/repos/{owner}/{repo}/git/trees",
        method="POST",
        data={"base_tree": base_tree, "tree": tree_items}
    )

    # Create commit
    new_commit = make_request(
        f"/repos/{owner}/{repo}/git/commits",
        method="POST",
        data={
            "message": message,
            "tree": tree["sha"],
            "parents": [current_sha]
        }
    )

    # Update reference
    make_request(
        f"/repos/{owner}/{repo}/git/refs/heads/{branch}",
        method="PATCH",
        data={"sha": new_commit["sha"]}
    )

    return {
        "sha": new_commit["sha"],
        "message": new_commit["message"],
        "files_pushed": list(files.keys()),
        "html_url": f"https://github.com/{owner}/{repo}/commit/{new_commit['sha']}"
    }


def create_branch(owner, repo, branch, from_branch=None):
    """Create new branch from existing branch."""
    # Get source branch SHA (try main, then master)
    source = from_branch
    if not source:
        try:
            ref = make_request(f"/repos/{owner}/{repo}/git/ref/heads/main")
            source = "main"
        except SystemExit:
            try:
                ref = make_request(f"/repos/{owner}/{repo}/git/ref/heads/master")
                source = "master"
            except SystemExit:
                error("Could not find main or master branch. Specify --from-branch.")
    else:
        ref = make_request(f"/repos/{owner}/{repo}/git/ref/heads/{source}")

    return make_request(
        f"/repos/{owner}/{repo}/git/refs",
        method="POST",
        data={
            "ref": f"refs/heads/{branch}",
            "sha": ref["object"]["sha"]
        }
    )


def list_branches(owner, repo, per_page=30, page=1):
    """List repository branches."""
    return make_request(
        f"/repos/{owner}/{repo}/branches",
        params={"per_page": per_page, "page": page}
    )


def get_repo(owner, repo):
    """Get repository details."""
    return make_request(f"/repos/{owner}/{repo}")


def create_repo(name, description=None, private=False, auto_init=False):
    """Create new repository for authenticated user."""
    data = {
        "name": name,
        "private": private,
        "auto_init": auto_init
    }
    if description:
        data["description"] = description

    return make_request("/user/repos", method="POST", data=data)


def fork_repo(owner, repo, organization=None):
    """Fork repository to user account or organization."""
    endpoint = f"/repos/{owner}/{repo}/forks"
    data = {}
    if organization:
        data["organization"] = organization

    return make_request(endpoint, method="POST", data=data if data else None)


def delete_file(owner, repo, path, message, sha, branch=None):
    """Delete a file from repository."""
    endpoint = f"/repos/{owner}/{repo}/contents/{path}"
    data = {
        "message": message,
        "sha": sha
    }
    if branch:
        data["branch"] = branch

    return make_request(endpoint, method="DELETE", data=data)


def main():
    parser = argparse.ArgumentParser(
        description="GitHub repository operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python repos.py get-file --owner octocat --repo Hello-World --path README.md
  python repos.py list-files --owner octocat --repo Hello-World --path src
  python repos.py create-branch --owner myuser --repo myrepo --branch feature-x
  python repos.py create-repo --name my-new-repo --private
        """
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # get-file
    p = subparsers.add_parser("get-file", help="Get file contents")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--path", required=True, help="File path")
    p.add_argument("--branch", help="Branch name (optional)")
    add_format_args(p)

    # list-files
    p = subparsers.add_parser("list-files", help="List directory contents")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--path", default="", help="Directory path (default: root)")
    p.add_argument("--branch", help="Branch name (optional)")
    add_format_args(p)

    # create-file
    p = subparsers.add_parser("create-file", help="Create or update file")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--path", required=True, help="File path")
    p.add_argument("--content", required=True, help="File content")
    p.add_argument("--message", required=True, help="Commit message")
    p.add_argument("--branch", help="Branch name (optional)")
    p.add_argument("--sha", help="Current file SHA (required for updates)")
    add_format_args(p)

    # push-files
    p = subparsers.add_parser("push-files", help="Push multiple files in one commit")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--branch", required=True, help="Target branch")
    p.add_argument("--message", required=True, help="Commit message")
    p.add_argument("--files", required=True,
                   help='JSON object of path:content pairs, e.g. \'{"file.txt": "content"}\'')
    add_format_args(p)

    # create-branch
    p = subparsers.add_parser("create-branch", help="Create new branch")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--branch", required=True, help="New branch name")
    p.add_argument("--from-branch", help="Source branch (default: main or master)")
    add_format_args(p)

    # list-branches
    p = subparsers.add_parser("list-branches", help="List repository branches")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    add_pagination_args(p)
    add_format_args(p)

    # get
    p = subparsers.add_parser("get", help="Get repository details")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    add_format_args(p)

    # create-repo
    p = subparsers.add_parser("create-repo", help="Create new repository")
    p.add_argument("--name", required=True, help="Repository name")
    p.add_argument("--description", help="Repository description")
    p.add_argument("--private", action="store_true", help="Make repository private")
    p.add_argument("--auto-init", action="store_true", help="Initialize with README")
    add_format_args(p)

    # fork
    p = subparsers.add_parser("fork", help="Fork repository")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--organization", help="Fork to organization instead of user")
    add_format_args(p)

    # delete-file
    p = subparsers.add_parser("delete-file", help="Delete file from repository")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--path", required=True, help="File path")
    p.add_argument("--message", required=True, help="Commit message")
    p.add_argument("--sha", required=True, help="Current file SHA")
    p.add_argument("--branch", help="Branch name (optional)")
    add_format_args(p)

    args = parser.parse_args()

    # Execute command
    if args.command == "get-file":
        result = get_file(args.owner, args.repo, args.path, args.branch)
    elif args.command == "list-files":
        result = list_files(args.owner, args.repo, args.path, args.branch)
    elif args.command == "create-file":
        result = create_file(args.owner, args.repo, args.path, args.content,
                            args.message, args.branch, args.sha)
    elif args.command == "push-files":
        try:
            files = json.loads(args.files)
        except json.JSONDecodeError as e:
            error(f"Invalid JSON for --files: {e}")
        result = push_files(args.owner, args.repo, args.branch, args.message, files)
    elif args.command == "create-branch":
        result = create_branch(args.owner, args.repo, args.branch, args.from_branch)
    elif args.command == "list-branches":
        result = list_branches(args.owner, args.repo, args.per_page, args.page)
    elif args.command == "get":
        result = get_repo(args.owner, args.repo)
    elif args.command == "create-repo":
        result = create_repo(args.name, args.description, args.private, args.auto_init)
    elif args.command == "fork":
        result = fork_repo(args.owner, args.repo, args.organization)
    elif args.command == "delete-file":
        result = delete_file(args.owner, args.repo, args.path, args.message,
                            args.sha, args.branch)

    output_json(result, args.format)


if __name__ == "__main__":
    main()
