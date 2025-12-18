#!/usr/bin/env python3
"""
GitHub Actions / Workflow operations.

Usage:
    python actions.py list-workflows --owner OWNER --repo REPO
    python actions.py list-runs --owner OWNER --repo REPO
    python actions.py get-run --owner OWNER --repo REPO --run-id RUN_ID
    python actions.py list-jobs --owner OWNER --repo REPO --run-id RUN_ID
    python actions.py get-logs --owner OWNER --repo REPO --run-id RUN_ID
    python actions.py rerun --owner OWNER --repo REPO --run-id RUN_ID
    python actions.py cancel --owner OWNER --repo REPO --run-id RUN_ID
    python actions.py dispatch --owner OWNER --repo REPO --workflow WORKFLOW --ref BRANCH
"""

import argparse
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from github_client import make_request, make_request_raw
from utils import output_json, add_pagination_args, add_format_args


def list_workflows(owner, repo, per_page=30, page=1):
    """List all workflows in repository."""
    return make_request(
        f"/repos/{owner}/{repo}/actions/workflows",
        params={"per_page": per_page, "page": page}
    )


def get_workflow(owner, repo, workflow_id):
    """Get specific workflow by ID or filename."""
    return make_request(f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}")


def list_runs(owner, repo, workflow_id=None, actor=None, branch=None, event=None,
              status=None, created=None, head_sha=None, per_page=30, page=1):
    """List workflow runs."""
    params = {
        "per_page": per_page,
        "page": page
    }
    if actor:
        params["actor"] = actor
    if branch:
        params["branch"] = branch
    if event:
        params["event"] = event
    if status:
        params["status"] = status
    if created:
        params["created"] = created
    if head_sha:
        params["head_sha"] = head_sha

    if workflow_id:
        endpoint = f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs"
    else:
        endpoint = f"/repos/{owner}/{repo}/actions/runs"

    return make_request(endpoint, params=params)


def get_run(owner, repo, run_id):
    """Get specific workflow run."""
    return make_request(f"/repos/{owner}/{repo}/actions/runs/{run_id}")


def list_jobs(owner, repo, run_id, filter_status=None, per_page=30, page=1):
    """List jobs for a workflow run."""
    params = {"per_page": per_page, "page": page}
    if filter_status:
        params["filter"] = filter_status

    return make_request(
        f"/repos/{owner}/{repo}/actions/runs/{run_id}/jobs",
        params=params
    )


def get_job(owner, repo, job_id):
    """Get specific job."""
    return make_request(f"/repos/{owner}/{repo}/actions/jobs/{job_id}")


def get_job_logs(owner, repo, job_id):
    """Get logs for a specific job.

    Returns the log content as text.
    """
    logs = make_request_raw(
        f"/repos/{owner}/{repo}/actions/jobs/{job_id}/logs",
        accept="application/vnd.github+json"
    )
    return {"job_id": job_id, "logs": logs.decode("utf-8", errors="replace")}


def get_run_logs(owner, repo, run_id, output_file=None):
    """Download logs for workflow run.

    Returns compressed log archive or saves to file.
    """
    logs = make_request_raw(
        f"/repos/{owner}/{repo}/actions/runs/{run_id}/logs",
        accept="application/vnd.github+json"
    )

    if output_file:
        with open(output_file, "wb") as f:
            f.write(logs)
        return {"saved_to": output_file, "size_bytes": len(logs)}
    else:
        return {"run_id": run_id, "size_bytes": len(logs),
                "note": "Use --output-file to save zip archive"}


def delete_run_logs(owner, repo, run_id):
    """Delete logs for a workflow run."""
    make_request(
        f"/repos/{owner}/{repo}/actions/runs/{run_id}/logs",
        method="DELETE"
    )
    return {"deleted": True, "run_id": run_id}


def rerun_workflow(owner, repo, run_id, failed_only=False):
    """Rerun a workflow or just failed jobs."""
    if failed_only:
        endpoint = f"/repos/{owner}/{repo}/actions/runs/{run_id}/rerun-failed-jobs"
    else:
        endpoint = f"/repos/{owner}/{repo}/actions/runs/{run_id}/rerun"

    make_request(endpoint, method="POST")
    return {"rerun_triggered": True, "run_id": run_id, "failed_only": failed_only}


def cancel_run(owner, repo, run_id):
    """Cancel a workflow run."""
    make_request(
        f"/repos/{owner}/{repo}/actions/runs/{run_id}/cancel",
        method="POST"
    )
    return {"cancelled": True, "run_id": run_id}


def delete_run(owner, repo, run_id):
    """Delete a workflow run."""
    make_request(
        f"/repos/{owner}/{repo}/actions/runs/{run_id}",
        method="DELETE"
    )
    return {"deleted": True, "run_id": run_id}


def dispatch_workflow(owner, repo, workflow_id, ref, inputs=None):
    """Trigger a workflow_dispatch event.

    Args:
        workflow_id: Workflow ID or filename (e.g., "ci.yml")
        ref: Branch or tag to run workflow on
        inputs: Dict of input values for the workflow
    """
    data = {"ref": ref}
    if inputs:
        data["inputs"] = inputs

    make_request(
        f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches",
        method="POST",
        data=data
    )
    return {"dispatched": True, "workflow": workflow_id, "ref": ref, "inputs": inputs}


def list_artifacts(owner, repo, run_id=None, per_page=30, page=1):
    """List artifacts for a run or repository."""
    params = {"per_page": per_page, "page": page}

    if run_id:
        endpoint = f"/repos/{owner}/{repo}/actions/runs/{run_id}/artifacts"
    else:
        endpoint = f"/repos/{owner}/{repo}/actions/artifacts"

    return make_request(endpoint, params=params)


def get_artifact(owner, repo, artifact_id):
    """Get artifact metadata."""
    return make_request(f"/repos/{owner}/{repo}/actions/artifacts/{artifact_id}")


def delete_artifact(owner, repo, artifact_id):
    """Delete an artifact."""
    make_request(
        f"/repos/{owner}/{repo}/actions/artifacts/{artifact_id}",
        method="DELETE"
    )
    return {"deleted": True, "artifact_id": artifact_id}


def main():
    parser = argparse.ArgumentParser(
        description="GitHub Actions operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python actions.py list-workflows --owner octocat --repo Hello-World
  python actions.py list-runs --owner octocat --repo Hello-World --status failure
  python actions.py get-run --owner octocat --repo Hello-World --run-id 12345
  python actions.py rerun --owner myuser --repo myrepo --run-id 12345 --failed-only
  python actions.py dispatch --owner myuser --repo myrepo --workflow ci.yml --ref main
        """
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list-workflows
    p = subparsers.add_parser("list-workflows", help="List workflows")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    add_pagination_args(p)
    add_format_args(p)

    # get-workflow
    p = subparsers.add_parser("get-workflow", help="Get workflow details")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--workflow-id", required=True, help="Workflow ID or filename")
    add_format_args(p)

    # list-runs
    p = subparsers.add_parser("list-runs", help="List workflow runs")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--workflow-id", help="Filter by workflow ID or filename")
    p.add_argument("--actor", help="Filter by actor (username)")
    p.add_argument("--branch", help="Filter by branch")
    p.add_argument("--event", help="Filter by event (push, pull_request, etc.)")
    p.add_argument("--status", choices=["queued", "in_progress", "completed",
                                         "waiting", "requested", "pending"],
                  help="Filter by status")
    p.add_argument("--created", help="Filter by creation date (e.g., >2024-01-01)")
    add_pagination_args(p)
    add_format_args(p)

    # get-run
    p = subparsers.add_parser("get-run", help="Get workflow run details")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--run-id", type=int, required=True, help="Run ID")
    add_format_args(p)

    # list-jobs
    p = subparsers.add_parser("list-jobs", help="List jobs in workflow run")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--run-id", type=int, required=True, help="Run ID")
    p.add_argument("--filter", dest="filter_status", choices=["latest", "all"],
                  help="Filter jobs")
    add_pagination_args(p)
    add_format_args(p)

    # get-job
    p = subparsers.add_parser("get-job", help="Get job details")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--job-id", type=int, required=True, help="Job ID")
    add_format_args(p)

    # get-job-logs
    p = subparsers.add_parser("get-job-logs", help="Get logs for a job")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--job-id", type=int, required=True, help="Job ID")
    add_format_args(p)

    # get-logs
    p = subparsers.add_parser("get-logs", help="Download run logs")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--run-id", type=int, required=True, help="Run ID")
    p.add_argument("--output-file", help="Save logs to file (zip)")
    add_format_args(p)

    # delete-logs
    p = subparsers.add_parser("delete-logs", help="Delete run logs")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--run-id", type=int, required=True, help="Run ID")
    add_format_args(p)

    # rerun
    p = subparsers.add_parser("rerun", help="Rerun workflow")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--run-id", type=int, required=True, help="Run ID")
    p.add_argument("--failed-only", action="store_true",
                  help="Only rerun failed jobs")
    add_format_args(p)

    # cancel
    p = subparsers.add_parser("cancel", help="Cancel workflow run")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--run-id", type=int, required=True, help="Run ID")
    add_format_args(p)

    # delete-run
    p = subparsers.add_parser("delete-run", help="Delete workflow run")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--run-id", type=int, required=True, help="Run ID")
    add_format_args(p)

    # dispatch
    p = subparsers.add_parser("dispatch", help="Trigger workflow_dispatch")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--workflow", required=True, help="Workflow ID or filename")
    p.add_argument("--ref", required=True, help="Branch or tag")
    p.add_argument("--inputs", help="JSON object of workflow inputs")
    add_format_args(p)

    # list-artifacts
    p = subparsers.add_parser("list-artifacts", help="List artifacts")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--run-id", type=int, help="Filter by run ID")
    add_pagination_args(p)
    add_format_args(p)

    # get-artifact
    p = subparsers.add_parser("get-artifact", help="Get artifact details")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--artifact-id", type=int, required=True, help="Artifact ID")
    add_format_args(p)

    # delete-artifact
    p = subparsers.add_parser("delete-artifact", help="Delete artifact")
    p.add_argument("--owner", required=True, help="Repository owner")
    p.add_argument("--repo", required=True, help="Repository name")
    p.add_argument("--artifact-id", type=int, required=True, help="Artifact ID")
    add_format_args(p)

    args = parser.parse_args()

    # Execute command
    if args.command == "list-workflows":
        result = list_workflows(args.owner, args.repo, args.per_page, args.page)
    elif args.command == "get-workflow":
        result = get_workflow(args.owner, args.repo, args.workflow_id)
    elif args.command == "list-runs":
        result = list_runs(args.owner, args.repo, args.workflow_id, args.actor,
                          args.branch, args.event, args.status, args.created,
                          None, args.per_page, args.page)
    elif args.command == "get-run":
        result = get_run(args.owner, args.repo, args.run_id)
    elif args.command == "list-jobs":
        result = list_jobs(args.owner, args.repo, args.run_id,
                          args.filter_status, args.per_page, args.page)
    elif args.command == "get-job":
        result = get_job(args.owner, args.repo, args.job_id)
    elif args.command == "get-job-logs":
        result = get_job_logs(args.owner, args.repo, args.job_id)
    elif args.command == "get-logs":
        result = get_run_logs(args.owner, args.repo, args.run_id, args.output_file)
    elif args.command == "delete-logs":
        result = delete_run_logs(args.owner, args.repo, args.run_id)
    elif args.command == "rerun":
        result = rerun_workflow(args.owner, args.repo, args.run_id, args.failed_only)
    elif args.command == "cancel":
        result = cancel_run(args.owner, args.repo, args.run_id)
    elif args.command == "delete-run":
        result = delete_run(args.owner, args.repo, args.run_id)
    elif args.command == "dispatch":
        inputs = json.loads(args.inputs) if args.inputs else None
        result = dispatch_workflow(args.owner, args.repo, args.workflow, args.ref, inputs)
    elif args.command == "list-artifacts":
        result = list_artifacts(args.owner, args.repo, args.run_id,
                               args.per_page, args.page)
    elif args.command == "get-artifact":
        result = get_artifact(args.owner, args.repo, args.artifact_id)
    elif args.command == "delete-artifact":
        result = delete_artifact(args.owner, args.repo, args.artifact_id)

    output_json(result, args.format)


if __name__ == "__main__":
    main()
