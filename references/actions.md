# GitHub Actions / Workflows

Operations for managing GitHub Actions workflows, runs, jobs, and artifacts.

## List Workflows

List all workflow definitions in a repository.

```bash
python scripts/actions.py list-workflows \
  --owner OWNER \
  --repo REPO
```

**Returns**: All workflow files and their IDs.

## Get Workflow

Get details about a specific workflow.

```bash
python scripts/actions.py get-workflow \
  --owner OWNER \
  --repo REPO \
  --workflow-id WORKFLOW_ID
```

**Note**: `workflow-id` can be the numeric ID or the filename (e.g., `ci.yml`).

## List Workflow Runs

List workflow runs with filtering options.

```bash
python scripts/actions.py list-runs \
  --owner OWNER \
  --repo REPO \
  [--workflow-id WORKFLOW_ID] \
  [--actor USERNAME] \
  [--branch BRANCH] \
  [--event push|pull_request|workflow_dispatch|...] \
  [--status queued|in_progress|completed|waiting] \
  [--created ">2024-01-01"] \
  [--per-page 30]
```

**Examples**:
```bash
# List failed runs
python scripts/actions.py list-runs --owner myuser --repo myrepo --status completed

# List runs for specific workflow
python scripts/actions.py list-runs --owner myuser --repo myrepo --workflow-id ci.yml

# List runs triggered by a user
python scripts/actions.py list-runs --owner myuser --repo myrepo --actor octocat
```

## Get Workflow Run

Get details of a specific workflow run.

```bash
python scripts/actions.py get-run \
  --owner OWNER \
  --repo REPO \
  --run-id RUN_ID
```

**Returns**: Run details including status, timing, conclusion, and trigger info.

## List Jobs

List all jobs in a workflow run.

```bash
python scripts/actions.py list-jobs \
  --owner OWNER \
  --repo REPO \
  --run-id RUN_ID \
  [--filter latest|all]
```

**Returns**: All jobs with their status, steps, and timing.

## Get Job

Get details of a specific job.

```bash
python scripts/actions.py get-job \
  --owner OWNER \
  --repo REPO \
  --job-id JOB_ID
```

## Get Job Logs

Get the logs for a specific job (readable text).

```bash
python scripts/actions.py get-job-logs \
  --owner OWNER \
  --repo REPO \
  --job-id JOB_ID
```

**Returns**: Job logs as text output.

## Download Run Logs

Download all logs for a workflow run as a zip archive.

```bash
python scripts/actions.py get-logs \
  --owner OWNER \
  --repo REPO \
  --run-id RUN_ID \
  [--output-file logs.zip]
```

**Example**:
```bash
python scripts/actions.py get-logs --owner myuser --repo myrepo --run-id 12345 --output-file run-logs.zip
```

## Delete Run Logs

Delete logs for a workflow run.

```bash
python scripts/actions.py delete-logs \
  --owner OWNER \
  --repo REPO \
  --run-id RUN_ID
```

## Rerun Workflow

Rerun a workflow or just the failed jobs.

```bash
python scripts/actions.py rerun \
  --owner OWNER \
  --repo REPO \
  --run-id RUN_ID \
  [--failed-only]
```

**Examples**:
```bash
# Rerun entire workflow
python scripts/actions.py rerun --owner myuser --repo myrepo --run-id 12345

# Rerun only failed jobs
python scripts/actions.py rerun --owner myuser --repo myrepo --run-id 12345 --failed-only
```

## Cancel Workflow Run

Cancel a running workflow.

```bash
python scripts/actions.py cancel \
  --owner OWNER \
  --repo REPO \
  --run-id RUN_ID
```

## Delete Workflow Run

Delete a workflow run from history.

```bash
python scripts/actions.py delete-run \
  --owner OWNER \
  --repo REPO \
  --run-id RUN_ID
```

## Trigger Workflow (workflow_dispatch)

Manually trigger a workflow that supports `workflow_dispatch`.

```bash
python scripts/actions.py dispatch \
  --owner OWNER \
  --repo REPO \
  --workflow WORKFLOW_FILE_OR_ID \
  --ref BRANCH \
  [--inputs '{"key": "value"}']
```

**Example**:
```bash
# Trigger deployment workflow
python scripts/actions.py dispatch \
  --owner myuser --repo myrepo \
  --workflow deploy.yml \
  --ref main \
  --inputs '{"environment": "production", "version": "1.2.3"}'
```

**Note**: The workflow must have `workflow_dispatch` trigger defined.

## Artifacts

### List Artifacts

List artifacts for a run or entire repository.

```bash
python scripts/actions.py list-artifacts \
  --owner OWNER \
  --repo REPO \
  [--run-id RUN_ID]
```

### Get Artifact

Get artifact metadata.

```bash
python scripts/actions.py get-artifact \
  --owner OWNER \
  --repo REPO \
  --artifact-id ARTIFACT_ID
```

### Delete Artifact

Delete an artifact.

```bash
python scripts/actions.py delete-artifact \
  --owner OWNER \
  --repo REPO \
  --artifact-id ARTIFACT_ID
```

## Common Workflows

### Check Why CI Failed

```bash
# 1. List recent runs
python scripts/actions.py list-runs --owner myuser --repo myrepo --status completed --per-page 5

# 2. Get run details
python scripts/actions.py get-run --owner myuser --repo myrepo --run-id 12345

# 3. List jobs to find failures
python scripts/actions.py list-jobs --owner myuser --repo myrepo --run-id 12345

# 4. Get logs for failed job
python scripts/actions.py get-job-logs --owner myuser --repo myrepo --job-id 67890
```

### Rerun Failed Jobs After Fix

```bash
# Push fix, then rerun failed jobs
python scripts/actions.py rerun --owner myuser --repo myrepo --run-id 12345 --failed-only
```

## Output Formats

All commands support `--format` with values:
- `json` (default) - Full JSON output
- `markdown` - Human-readable markdown
- `minimal` - Compact JSON (no whitespace)

## Required Token Scopes

- `workflow` - Required for workflow operations
- `repo` - Required for private repository access
