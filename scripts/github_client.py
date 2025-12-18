#!/usr/bin/env python3
"""
Core GitHub API client with authentication and common utilities.

Usage:
    python github_client.py --check-auth
    python github_client.py --rate-limit
"""

import os
import sys
import json
import argparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode

GITHUB_API = "https://api.github.com"


def get_token():
    """Get GitHub token from environment."""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Error: GITHUB_TOKEN environment variable not set", file=sys.stderr)
        print("Set it with: export GITHUB_TOKEN=your_token", file=sys.stderr)
        sys.exit(1)
    return token


def make_request(endpoint, method="GET", data=None, params=None, accept=None):
    """Make authenticated request to GitHub API.

    Args:
        endpoint: API endpoint (e.g., "/repos/owner/repo")
        method: HTTP method (GET, POST, PUT, PATCH, DELETE)
        data: Request body as dict (will be JSON-encoded)
        params: Query parameters as dict
        accept: Accept header value (defaults to GitHub JSON API)

    Returns:
        Parsed JSON response as dict/list, or None for 204 responses

    Raises:
        SystemExit on API errors
    """
    token = get_token()

    url = f"{GITHUB_API}{endpoint}"
    if params:
        # Filter out None values
        params = {k: v for k, v in params.items() if v is not None}
        if params:
            url += "?" + urlencode(params)

    headers = {
        "Authorization": f"token {token}",
        "Accept": accept or "application/vnd.github+json",
        "User-Agent": "Claude-GitHub-Skill",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    if data is not None:
        headers["Content-Type"] = "application/json"

    body = json.dumps(data).encode() if data else None

    req = Request(url, data=body, headers=headers, method=method)

    try:
        with urlopen(req) as response:
            if response.status == 204:
                return None
            return json.loads(response.read().decode())
    except HTTPError as e:
        handle_error(e)
    except URLError as e:
        print(f"Network error: {e.reason}", file=sys.stderr)
        sys.exit(1)


def make_request_raw(endpoint, method="GET", params=None, accept=None):
    """Make request and return raw bytes (for binary content like logs)."""
    token = get_token()

    url = f"{GITHUB_API}{endpoint}"
    if params:
        params = {k: v for k, v in params.items() if v is not None}
        if params:
            url += "?" + urlencode(params)

    headers = {
        "Authorization": f"token {token}",
        "Accept": accept or "application/vnd.github+json",
        "User-Agent": "Claude-GitHub-Skill",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    req = Request(url, headers=headers, method=method)

    try:
        with urlopen(req) as response:
            return response.read()
    except HTTPError as e:
        handle_error(e)
    except URLError as e:
        print(f"Network error: {e.reason}", file=sys.stderr)
        sys.exit(1)


def handle_error(http_error):
    """Parse and handle GitHub API errors with actionable messages."""
    try:
        error_body = http_error.read().decode()
        try:
            error_data = json.loads(error_body)
            message = error_data.get("message", error_body)
        except json.JSONDecodeError:
            message = error_body

        code = http_error.code

        if code == 401:
            print("Error 401: Authentication failed", file=sys.stderr)
            print("Check your GITHUB_TOKEN is valid and not expired.", file=sys.stderr)
        elif code == 403:
            if "rate limit" in message.lower():
                print("Error 403: Rate limit exceeded", file=sys.stderr)
                print("Wait before retrying or use a token with higher limits.", file=sys.stderr)
            else:
                print(f"Error 403: Access denied - {message}", file=sys.stderr)
                print("Check token scopes and repository permissions.", file=sys.stderr)
        elif code == 404:
            print(f"Error 404: Resource not found - {message}", file=sys.stderr)
            print("Verify owner, repo, and resource exist and you have access.", file=sys.stderr)
        elif code == 422:
            print(f"Error 422: Validation failed - {message}", file=sys.stderr)
            if isinstance(error_data, dict) and "errors" in error_data:
                for err in error_data["errors"]:
                    if isinstance(err, dict):
                        field = err.get("field", "unknown")
                        msg = err.get("message", str(err))
                        print(f"  - {field}: {msg}", file=sys.stderr)
                    else:
                        print(f"  - {err}", file=sys.stderr)
        else:
            print(f"Error {code}: {message}", file=sys.stderr)

        sys.exit(1)
    except Exception as ex:
        print(f"Error {http_error.code}: Failed to parse error response", file=sys.stderr)
        sys.exit(1)


def check_auth():
    """Verify authentication works and show user info."""
    result = make_request("/user")
    print(f"Authenticated as: {result['login']}")
    if result.get('name'):
        print(f"Name: {result['name']}")
    if result.get('email'):
        print(f"Email: {result['email']}")
    print(f"Public repos: {result.get('public_repos', 0)}")
    print(f"Private repos: {result.get('total_private_repos', 0)}")
    return result


def get_rate_limit():
    """Get current rate limit status."""
    result = make_request("/rate_limit")

    core = result['resources']['core']
    search = result['resources']['search']
    graphql = result['resources'].get('graphql', {})

    print("Rate Limit Status:")
    print(f"  Core API:    {core['remaining']:>5}/{core['limit']} remaining")
    print(f"  Search API:  {search['remaining']:>5}/{search['limit']} remaining")
    if graphql:
        print(f"  GraphQL API: {graphql['remaining']:>5}/{graphql['limit']} remaining")

    # Show reset time if limits are low
    import time
    if core['remaining'] < 100:
        reset_time = time.strftime('%H:%M:%S', time.localtime(core['reset']))
        print(f"\n  Core API resets at: {reset_time}")

    return result


def main():
    parser = argparse.ArgumentParser(
        description="GitHub API client utilities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python github_client.py --check-auth    # Verify token works
  python github_client.py --rate-limit    # Show API rate limits
        """
    )
    parser.add_argument("--check-auth", action="store_true",
                       help="Check authentication and show user info")
    parser.add_argument("--rate-limit", action="store_true",
                       help="Show current rate limit status")

    args = parser.parse_args()

    if args.check_auth:
        check_auth()
    elif args.rate_limit:
        get_rate_limit()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
