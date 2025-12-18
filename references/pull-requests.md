# Pull Request Operations

Operations for creating, reviewing, and managing pull requests.

## List Pull Requests

List PRs in a repository with filtering options.

```bash
python scripts/pull_requests.py list \
  --owner OWNER \
  --repo REPO \
  [--state open|closed|all] \
  [--head "user:branch"] \
  [--base "main"] \
  [--sort created|updated|popularity|long-running] \
  [--direction asc|desc] \
  [--per-page 30]
```

**Examples**:
```bash
# List open PRs
python scripts/pull_requests.py list --owner octocat --repo Hello-World

# List PRs targeting main branch
python scripts/pull_requests.py list --owner octocat --repo Hello-World --base main
```

## Get Pull Request

Retrieve full details of a PR including merge status and review state.

```bash
python scripts/pull_requests.py get \
  --owner OWNER \
  --repo REPO \
  --number PR_NUMBER
```

**Returns**: PR details, merge status, review requirements, CI status.

## Create Pull Request

Create a new pull request.

```bash
python scripts/pull_requests.py create \
  --owner OWNER \
  --repo REPO \
  --title "PR title" \
  --head "feature-branch" \
  --base "main" \
  [--body "PR description"] \
  [--draft]
```

**Example**:
```bash
python scripts/pull_requests.py create \
  --owner myuser --repo myrepo \
  --title "Add user authentication" \
  --head feature-auth \
  --base main \
  --body "## Changes\n- Added login endpoint\n- Added JWT validation\n\n## Testing\n- Added unit tests for auth module"
```

## Update Pull Request

Update PR title, description, or state.

```bash
python scripts/pull_requests.py update \
  --owner OWNER \
  --repo REPO \
  --number PR_NUMBER \
  [--title "New title"] \
  [--body "New description"] \
  [--state open|closed] \
  [--base "new-base"]
```

## Get PR Files

List all files changed in a PR with diff information.

```bash
python scripts/pull_requests.py files \
  --owner OWNER \
  --repo REPO \
  --number PR_NUMBER
```

**Returns**: List of files with status (added/modified/removed), additions, deletions, and patch.

## Get PR Commits

List all commits in a PR.

```bash
python scripts/pull_requests.py commits \
  --owner OWNER \
  --repo REPO \
  --number PR_NUMBER
```

## Merge Pull Request

Merge a PR using specified merge method.

```bash
python scripts/pull_requests.py merge \
  --owner OWNER \
  --repo REPO \
  --number PR_NUMBER \
  [--method merge|squash|rebase] \
  [--commit-title "Merge title"] \
  [--commit-message "Merge message"] \
  [--sha HEAD_SHA]
```

**Examples**:
```bash
# Regular merge
python scripts/pull_requests.py merge --owner myuser --repo myrepo --number 42

# Squash merge with custom message
python scripts/pull_requests.py merge \
  --owner myuser --repo myrepo --number 42 \
  --method squash \
  --commit-title "feat: Add user authentication (#42)"
```

## Check Mergeable Status

Check if a PR can be merged.

```bash
python scripts/pull_requests.py check-mergeable \
  --owner OWNER \
  --repo REPO \
  --number PR_NUMBER
```

**Returns**: `mergeable`, `mergeable_state`, `rebaseable` status.

## Update PR Branch

Update PR branch with latest changes from base branch.

```bash
python scripts/pull_requests.py update-branch \
  --owner OWNER \
  --repo REPO \
  --number PR_NUMBER
```

## Get CI/Check Status

Get combined status of all CI checks and status checks.

```bash
python scripts/pull_requests.py status \
  --owner OWNER \
  --repo REPO \
  --number PR_NUMBER
```

**Returns**: Overall state (success/failure/pending), individual check runs and statuses.

## Reviews

### List Reviews

List all reviews on a PR.

```bash
python scripts/pull_requests.py reviews \
  --owner OWNER \
  --repo REPO \
  --number PR_NUMBER
```

### Create Review

Submit a review (approve, request changes, or comment).

```bash
python scripts/pull_requests.py review \
  --owner OWNER \
  --repo REPO \
  --number PR_NUMBER \
  --event APPROVE|REQUEST_CHANGES|COMMENT \
  [--body "Review comment"]
```

**Examples**:
```bash
# Approve PR
python scripts/pull_requests.py review \
  --owner myuser --repo myrepo --number 42 \
  --event APPROVE \
  --body "LGTM! Great work on the tests."

# Request changes
python scripts/pull_requests.py review \
  --owner myuser --repo myrepo --number 42 \
  --event REQUEST_CHANGES \
  --body "Please add error handling for the edge case on line 45."
```

### Dismiss Review

Dismiss a review.

```bash
python scripts/pull_requests.py dismiss-review \
  --owner OWNER \
  --repo REPO \
  --number PR_NUMBER \
  --review-id REVIEW_ID \
  --message "Dismissal reason"
```

## Reviewer Management

### Request Reviewers

Request reviews from users or teams.

```bash
python scripts/pull_requests.py request-reviewers \
  --owner OWNER \
  --repo REPO \
  --number PR_NUMBER \
  [--reviewers "user1,user2"] \
  [--team-reviewers "team-slug"]
```

### Remove Reviewers

Remove requested reviewers.

```bash
python scripts/pull_requests.py remove-reviewers \
  --owner OWNER \
  --repo REPO \
  --number PR_NUMBER \
  --reviewers "user1"
```

## Comments

### Add Comment

Add a comment to a PR.

```bash
python scripts/pull_requests.py comment \
  --owner OWNER \
  --repo REPO \
  --number PR_NUMBER \
  --body "Comment text"
```

### List Comments

List all comments on a PR.

```bash
python scripts/pull_requests.py list-comments \
  --owner OWNER \
  --repo REPO \
  --number PR_NUMBER
```

## Output Formats

All commands support `--format` with values:
- `json` (default) - Full JSON output
- `markdown` - Human-readable markdown
- `minimal` - Compact JSON (no whitespace)
