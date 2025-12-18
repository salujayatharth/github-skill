#!/usr/bin/env python3
"""
Code security operations (Dependabot and Code Scanning).

Usage:
    python code_security.py dependabot-alerts --owner OWNER --repo REPO
    python code_security.py get-dependabot-alert --owner OWNER --repo REPO --alert-number NUM
    python code_security.py update-dependabot-alert --owner OWNER --repo REPO --alert-number NUM --state dismissed
    python code_security.py code-scanning-alerts --owner OWNER --repo REPO
    python code_security.py get-code-scanning-alert --owner OWNER --repo REPO --alert-number NUM
    python code_security.py secret-scanning-alerts --owner OWNER --repo REPO
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from github_client import make_request
from utils import output_json, add_pagination_args, add_format_args


# ============================================================================
# Dependabot Alerts
# ============================================================================

def list_dependabot_alerts(owner, repo, state=None, severity=None, ecosystem=None,
                           package=None, scope=None, sort="created", direction="desc",
                           per_page=30, page=1):
    """List Dependabot alerts for a repository."""
    params = {
        "sort": sort,
        "direction": direction,
        "per_page": per_page,
        "page": page
    }
    if state:
        params["state"] = state
    if severity:
        params["severity"] = severity
    if ecosystem:
        params["ecosystem"] = ecosystem
    if package:
        params["package"] = package
    if scope:
        params["scope"] = scope

    return make_request(f"/repos/{owner}/{repo}/dependabot/alerts", params=params)


def get_dependabot_alert(owner, repo, alert_number):
    """Get a specific Dependabot alert."""
    return make_request(f"/repos/{owner}/{repo}/dependabot/alerts/{alert_number}")


def update_dependabot_alert(owner, repo, alert_number, state, dismissed_reason=None,
                            dismissed_comment=None):
    """Update Dependabot alert state.

    Args:
        state: "dismissed" or "open"
        dismissed_reason: Required when dismissing. One of:
            fix_started, inaccurate, no_bandwidth, not_used, tolerable_risk
        dismissed_comment: Optional comment when dismissing
    """
    data = {"state": state}
    if dismissed_reason:
        data["dismissed_reason"] = dismissed_reason
    if dismissed_comment:
        data["dismissed_comment"] = dismissed_comment

    return make_request(
        f"/repos/{owner}/{repo}/dependabot/alerts/{alert_number}",
        method="PATCH",
        data=data
    )


# ============================================================================
# Code Scanning Alerts
# ============================================================================

def list_code_scanning_alerts(owner, repo, state=None, severity=None, tool_name=None,
                               ref=None, sort="created", direction="desc",
                               per_page=30, page=1):
    """List code scanning alerts for a repository."""
    params = {
        "sort": sort,
        "direction": direction,
        "per_page": per_page,
        "page": page
    }
    if state:
        params["state"] = state
    if severity:
        params["severity"] = severity
    if tool_name:
        params["tool_name"] = tool_name
    if ref:
        params["ref"] = ref

    return make_request(f"/repos/{owner}/{repo}/code-scanning/alerts", params=params)


def get_code_scanning_alert(owner, repo, alert_number):
    """Get a specific code scanning alert."""
    return make_request(f"/repos/{owner}/{repo}/code-scanning/alerts/{alert_number}")


def update_code_scanning_alert(owner, repo, alert_number, state, dismissed_reason=None,
                                dismissed_comment=None):
    """Update code scanning alert state.

    Args:
        state: "dismissed" or "open"
        dismissed_reason: Required when dismissing. One of:
            false positive, won't fix, used in tests
        dismissed_comment: Optional comment when dismissing
    """
    data = {"state": state}
    if dismissed_reason:
        data["dismissed_reason"] = dismissed_reason
    if dismissed_comment:
        data["dismissed_comment"] = dismissed_comment

    return make_request(
        f"/repos/{owner}/{repo}/code-scanning/alerts/{alert_number}",
        method="PATCH",
        data=data
    )


def list_code_scanning_analyses(owner, repo, ref=None, tool_name=None,
                                 per_page=30, page=1):
    """List code scanning analyses for a repository."""
    params = {"per_page": per_page, "page": page}
    if ref:
        params["ref"] = ref
    if tool_name:
        params["tool_name"] = tool_name

    return make_request(f"/repos/{owner}/{repo}/code-scanning/analyses", params=params)


def get_code_scanning_analysis(owner, repo, analysis_id):
    """Get a specific code scanning analysis."""
    return make_request(f"/repos/{owner}/{repo}/code-scanning/analyses/{analysis_id}")


# ============================================================================
# Secret Scanning Alerts
# ============================================================================

def list_secret_scanning_alerts(owner, repo, state=None, secret_type=None,
                                 resolution=None, sort="created", direction="desc",
                                 per_page=30, page=1):
    """List secret scanning alerts for a repository."""
    params = {
        "sort": sort,
        "direction": direction,
        "per_page": per_page,
        "page": page
    }
    if state:
        params["state"] = state
    if secret_type:
        params["secret_type"] = secret_type
    if resolution:
        params["resolution"] = resolution

    return make_request(f"/repos/{owner}/{repo}/secret-scanning/alerts", params=params)


def get_secret_scanning_alert(owner, repo, alert_number):
    """Get a specific secret scanning alert."""
    return make_request(f"/repos/{owner}/{repo}/secret-scanning/alerts/{alert_number}")


def update_secret_scanning_alert(owner, repo, alert_number, state, resolution=None,
                                  resolution_comment=None):
    """Update secret scanning alert state.

    Args:
        state: "resolved" or "open"
        resolution: Required when resolving. One of:
            false_positive, wont_fix, revoked, used_in_tests, pattern_deleted, pattern_edited
    """
    data = {"state": state}
    if resolution:
        data["resolution"] = resolution
    if resolution_comment:
        data["resolution_comment"] = resolution_comment

    return make_request(
        f"/repos/{owner}/{repo}/secret-scanning/alerts/{alert_number}",
        method="PATCH",
        data=data
    )


def list_secret_scanning_locations(owner, repo, alert_number, per_page=30, page=1):
    """List locations for a secret scanning alert."""
    return make_request(
        f"/repos/{owner}/{repo}/secret-scanning/alerts/{alert_number}/locations",
        params={"per_page": per_page, "page": page}
    )


# ============================================================================
# Security Overview
# ============================================================================

def get_security_advisories(owner, repo, per_page=30, page=1):
    """List repository security advisories."""
    return make_request(
        f"/repos/{owner}/{repo}/security-advisories",
        params={"per_page": per_page, "page": page}
    )


def main():
    parser = argparse.ArgumentParser(
        description="GitHub code security operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python code_security.py dependabot-alerts --owner myuser --repo myrepo --severity critical,high
  python code_security.py get-dependabot-alert --owner myuser --repo myrepo --alert-number 1
  python code_security.py update-dependabot-alert --owner myuser --repo myrepo --alert-number 1 --state dismissed --reason not_used
  python code_security.py code-scanning-alerts --owner myuser --repo myrepo --state open
  python code_security.py secret-scanning-alerts --owner myuser --repo myrepo
        """
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # dependabot-alerts
    p = subparsers.add_parser("dependabot-alerts", help="List Dependabot alerts")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--state", choices=["open", "dismissed", "fixed"],
                  help="Filter by state")
    p.add_argument("--severity", help="Filter by severity (critical,high,medium,low)")
    p.add_argument("--ecosystem", help="Filter by ecosystem (npm,pip,maven,...)")
    p.add_argument("--package", help="Filter by package name")
    p.add_argument("--scope", choices=["development", "runtime"],
                  help="Filter by dependency scope")
    p.add_argument("--sort", choices=["created", "updated"], default="created")
    p.add_argument("--direction", choices=["asc", "desc"], default="desc")
    add_pagination_args(p)
    add_format_args(p)

    # get-dependabot-alert
    p = subparsers.add_parser("get-dependabot-alert", help="Get Dependabot alert")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--alert-number", type=int, required=True, help="Alert number")
    add_format_args(p)

    # update-dependabot-alert
    p = subparsers.add_parser("update-dependabot-alert", help="Update Dependabot alert")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--alert-number", type=int, required=True, help="Alert number")
    p.add_argument("--state", required=True, choices=["dismissed", "open"],
                  help="New state")
    p.add_argument("--reason", choices=["fix_started", "inaccurate", "no_bandwidth",
                                         "not_used", "tolerable_risk"],
                  help="Dismissal reason (required when dismissing)")
    p.add_argument("--comment", help="Dismissal comment")
    add_format_args(p)

    # code-scanning-alerts
    p = subparsers.add_parser("code-scanning-alerts", help="List code scanning alerts")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--state", choices=["open", "closed", "dismissed", "fixed"],
                  help="Filter by state")
    p.add_argument("--severity", help="Filter by severity (critical,high,medium,low,warning,note,error)")
    p.add_argument("--tool-name", help="Filter by tool (e.g., CodeQL)")
    p.add_argument("--ref", help="Filter by Git ref (branch/tag)")
    p.add_argument("--sort", choices=["created", "updated"], default="created")
    p.add_argument("--direction", choices=["asc", "desc"], default="desc")
    add_pagination_args(p)
    add_format_args(p)

    # get-code-scanning-alert
    p = subparsers.add_parser("get-code-scanning-alert", help="Get code scanning alert")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--alert-number", type=int, required=True, help="Alert number")
    add_format_args(p)

    # update-code-scanning-alert
    p = subparsers.add_parser("update-code-scanning-alert", help="Update code scanning alert")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--alert-number", type=int, required=True, help="Alert number")
    p.add_argument("--state", required=True, choices=["dismissed", "open"],
                  help="New state")
    p.add_argument("--reason", choices=["false positive", "won't fix", "used in tests"],
                  help="Dismissal reason (required when dismissing)")
    p.add_argument("--comment", help="Dismissal comment")
    add_format_args(p)

    # code-scanning-analyses
    p = subparsers.add_parser("code-scanning-analyses", help="List code scanning analyses")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--ref", help="Filter by Git ref")
    p.add_argument("--tool-name", help="Filter by tool name")
    add_pagination_args(p)
    add_format_args(p)

    # secret-scanning-alerts
    p = subparsers.add_parser("secret-scanning-alerts", help="List secret scanning alerts")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--state", choices=["open", "resolved"], help="Filter by state")
    p.add_argument("--secret-type", help="Filter by secret type")
    p.add_argument("--resolution", help="Filter by resolution")
    p.add_argument("--sort", choices=["created", "updated"], default="created")
    p.add_argument("--direction", choices=["asc", "desc"], default="desc")
    add_pagination_args(p)
    add_format_args(p)

    # get-secret-scanning-alert
    p = subparsers.add_parser("get-secret-scanning-alert", help="Get secret scanning alert")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--alert-number", type=int, required=True, help="Alert number")
    add_format_args(p)

    # update-secret-scanning-alert
    p = subparsers.add_parser("update-secret-scanning-alert", help="Update secret scanning alert")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--alert-number", type=int, required=True, help="Alert number")
    p.add_argument("--state", required=True, choices=["resolved", "open"],
                  help="New state")
    p.add_argument("--resolution", choices=["false_positive", "wont_fix", "revoked",
                                             "used_in_tests", "pattern_deleted", "pattern_edited"],
                  help="Resolution type (required when resolving)")
    p.add_argument("--comment", help="Resolution comment")
    add_format_args(p)

    # secret-scanning-locations
    p = subparsers.add_parser("secret-scanning-locations", help="List secret locations")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--alert-number", type=int, required=True, help="Alert number")
    add_pagination_args(p)
    add_format_args(p)

    # security-advisories
    p = subparsers.add_parser("security-advisories", help="List security advisories")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    add_pagination_args(p)
    add_format_args(p)

    args = parser.parse_args()

    # Execute command
    if args.command == "dependabot-alerts":
        result = list_dependabot_alerts(args.owner, args.repo, args.state,
                                        args.severity, args.ecosystem, args.package,
                                        args.scope, args.sort, args.direction,
                                        args.per_page, args.page)
    elif args.command == "get-dependabot-alert":
        result = get_dependabot_alert(args.owner, args.repo, args.alert_number)
    elif args.command == "update-dependabot-alert":
        result = update_dependabot_alert(args.owner, args.repo, args.alert_number,
                                         args.state, args.reason, args.comment)
    elif args.command == "code-scanning-alerts":
        result = list_code_scanning_alerts(args.owner, args.repo, args.state,
                                           args.severity, args.tool_name, args.ref,
                                           args.sort, args.direction,
                                           args.per_page, args.page)
    elif args.command == "get-code-scanning-alert":
        result = get_code_scanning_alert(args.owner, args.repo, args.alert_number)
    elif args.command == "update-code-scanning-alert":
        result = update_code_scanning_alert(args.owner, args.repo, args.alert_number,
                                            args.state, args.reason, args.comment)
    elif args.command == "code-scanning-analyses":
        result = list_code_scanning_analyses(args.owner, args.repo, args.ref,
                                             args.tool_name, args.per_page, args.page)
    elif args.command == "secret-scanning-alerts":
        result = list_secret_scanning_alerts(args.owner, args.repo, args.state,
                                             args.secret_type, args.resolution,
                                             args.sort, args.direction,
                                             args.per_page, args.page)
    elif args.command == "get-secret-scanning-alert":
        result = get_secret_scanning_alert(args.owner, args.repo, args.alert_number)
    elif args.command == "update-secret-scanning-alert":
        result = update_secret_scanning_alert(args.owner, args.repo, args.alert_number,
                                              args.state, args.resolution, args.comment)
    elif args.command == "secret-scanning-locations":
        result = list_secret_scanning_locations(args.owner, args.repo, args.alert_number,
                                                args.per_page, args.page)
    elif args.command == "security-advisories":
        result = get_security_advisories(args.owner, args.repo, args.per_page, args.page)

    output_json(result, args.format)


if __name__ == "__main__":
    main()
