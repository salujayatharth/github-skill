#!/usr/bin/env python3
"""Shared utilities for GitHub skill scripts."""

import json
import sys


def output_json(data, format_type="json"):
    """Output data in requested format.

    Args:
        data: Data to output (dict or list)
        format_type: Output format - "json", "markdown", or "minimal"
    """
    if format_type == "json":
        print(json.dumps(data, indent=2))
    elif format_type == "minimal":
        print(json.dumps(data, separators=(',', ':')))
    elif format_type == "markdown":
        print(format_as_markdown(data))
    else:
        print(json.dumps(data, indent=2))


def format_as_markdown(data):
    """Convert API response to readable markdown."""
    if isinstance(data, list):
        if not data:
            return "_No results_"
        return "\n\n---\n\n".join([format_item(item) for item in data])
    return format_item(data)


def format_item(item):
    """Format single item as markdown."""
    if not isinstance(item, dict):
        return str(item)

    lines = []

    # Handle common GitHub object types
    if "html_url" in item:
        title = item.get("title") or item.get("name") or item.get("login") or item.get("full_name")
        if title:
            lines.append(f"### [{title}]({item['html_url']})")
        else:
            lines.append(f"**URL**: {item['html_url']}")

    # Format key fields based on object type
    if "number" in item:  # Issue or PR
        lines.append(f"**#{item['number']}** - {item.get('state', 'unknown')}")
        if item.get("body"):
            body = item["body"][:200] + "..." if len(item.get("body", "")) > 200 else item.get("body", "")
            lines.append(f"\n{body}")
        if item.get("labels"):
            labels = ", ".join([l.get("name", str(l)) if isinstance(l, dict) else str(l) for l in item["labels"]])
            lines.append(f"**Labels**: {labels}")
        if item.get("assignees"):
            assignees = ", ".join([a.get("login", str(a)) if isinstance(a, dict) else str(a) for a in item["assignees"]])
            lines.append(f"**Assignees**: {assignees}")

    elif "sha" in item:  # Commit
        sha = item["sha"][:7]
        msg = item.get("commit", {}).get("message", item.get("message", ""))
        if msg:
            msg = msg.split("\n")[0]  # First line only
        lines.append(f"**{sha}**: {msg}")

    elif "path" in item and "type" in item:  # File/directory
        icon = "📁" if item["type"] == "dir" else "📄"
        lines.append(f"{icon} `{item['path']}`")

    elif "login" in item:  # User
        lines.append(f"**@{item['login']}**")
        if item.get("name"):
            lines.append(f"Name: {item['name']}")

    elif "full_name" in item:  # Repository
        lines.append(f"**{item['full_name']}**")
        if item.get("description"):
            lines.append(item["description"])
        stars = item.get("stargazers_count", 0)
        forks = item.get("forks_count", 0)
        lines.append(f"⭐ {stars} | 🍴 {forks}")

    elif "decoded_content" in item:  # File content
        lines.append(f"**File**: `{item.get('path', 'unknown')}`")
        lines.append(f"**Size**: {item.get('size', 0)} bytes")
        lines.append(f"\n```\n{item['decoded_content'][:1000]}")
        if len(item.get('decoded_content', '')) > 1000:
            lines.append("... (truncated)")
        lines.append("```")

    else:
        # Generic formatting for unknown types
        for key, value in item.items():
            if key in ("url", "node_id", "events_url", "hooks_url"):
                continue  # Skip internal URLs
            if isinstance(value, (dict, list)):
                if value:  # Only show non-empty
                    lines.append(f"**{key}**: {json.dumps(value, indent=2)[:100]}...")
            elif value is not None:
                lines.append(f"**{key}**: {value}")

    return "\n".join(lines) if lines else str(item)


def add_pagination_args(parser):
    """Add common pagination arguments to argparse parser."""
    parser.add_argument("--per-page", type=int, default=30,
                       help="Results per page (max 100, default 30)")
    parser.add_argument("--page", type=int, default=1,
                       help="Page number (default 1)")


def add_format_args(parser):
    """Add output format arguments to argparse parser."""
    parser.add_argument("--format", choices=["json", "markdown", "minimal"],
                       default="json",
                       help="Output format (default: json)")


def get_pagination_params(args):
    """Extract pagination params from parsed args as dict."""
    return {
        "per_page": min(args.per_page, 100),
        "page": args.page
    }


def add_common_args(parser):
    """Add both pagination and format arguments."""
    add_pagination_args(parser)
    add_format_args(parser)


def error(message):
    """Print error message to stderr and exit."""
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(1)
