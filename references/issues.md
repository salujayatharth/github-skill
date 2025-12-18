# Issue Management

Operations for creating, updating, and managing GitHub issues.

## List Issues

List issues in a repository with filtering options.

```bash
python scripts/issues.py list \
  --owner OWNER \
  --repo REPO \
  [--state open|closed|all] \
  [--labels "bug,enhancement"] \
  [--assignee USERNAME] \
  [--creator USERNAME] \
  [--mentioned USERNAME] \
  [--sort created|updated|comments] \
  [--direction asc|desc] \
  [--since "2024-01-01T00:00:00Z"] \
  [--per-page 30] \
  [--page 1]
```

**Examples**:
```bash
# List open bugs
python scripts/issues.py list --owner octocat --repo Hello-World --labels bug

# List issues assigned to a user
python scripts/issues.py list --owner octocat --repo Hello-World --assignee octocat

# List recently updated issues
python scripts/issues.py list --owner octocat --repo Hello-World --sort updated --direction desc
```

## Get Single Issue

Retrieve full details of a specific issue.

```bash
python scripts/issues.py get \
  --owner OWNER \
  --repo REPO \
  --number ISSUE_NUMBER
```

**Returns**: Full issue details including body, labels, assignees, milestone, and reactions.

## Create Issue

Create a new issue in a repository.

```bash
python scripts/issues.py create \
  --owner OWNER \
  --repo REPO \
  --title "Issue title" \
  [--body "Issue description"] \
  [--labels "bug,priority:high"] \
  [--assignees "user1,user2"] \
  [--milestone MILESTONE_NUMBER]
```

**Example**:
```bash
python scripts/issues.py create \
  --owner myuser --repo myrepo \
  --title "Login button not working" \
  --body "Steps to reproduce:\n1. Go to login page\n2. Click login\n\nExpected: Login form appears\nActual: Nothing happens" \
  --labels "bug,frontend" \
  --assignees "devuser"
```

## Update Issue

Update an existing issue's properties.

```bash
python scripts/issues.py update \
  --owner OWNER \
  --repo REPO \
  --number ISSUE_NUMBER \
  [--title "New title"] \
  [--body "New description"] \
  [--state open|closed] \
  [--state-reason completed|not_planned|reopened] \
  [--labels "new-label"] \
  [--assignees "user1"]
```

**Examples**:
```bash
# Close an issue as completed
python scripts/issues.py update \
  --owner myuser --repo myrepo --number 42 \
  --state closed --state-reason completed

# Close as won't fix
python scripts/issues.py update \
  --owner myuser --repo myrepo --number 42 \
  --state closed --state-reason not_planned

# Reassign and relabel
python scripts/issues.py update \
  --owner myuser --repo myrepo --number 42 \
  --assignees "newuser" --labels "in-progress"
```

## Add Comment

Add a comment to an issue.

```bash
python scripts/issues.py comment \
  --owner OWNER \
  --repo REPO \
  --number ISSUE_NUMBER \
  --body "Comment text"
```

**Example**:
```bash
python scripts/issues.py comment \
  --owner myuser --repo myrepo --number 42 \
  --body "I've started looking into this. Will update with findings soon."
```

## List Comments

List all comments on an issue.

```bash
python scripts/issues.py list-comments \
  --owner OWNER \
  --repo REPO \
  --number ISSUE_NUMBER \
  [--since "2024-01-01T00:00:00Z"] \
  [--per-page 30]
```

## Update Comment

Edit an existing comment.

```bash
python scripts/issues.py update-comment \
  --owner OWNER \
  --repo REPO \
  --comment-id COMMENT_ID \
  --body "Updated comment text"
```

## Delete Comment

Delete a comment from an issue.

```bash
python scripts/issues.py delete-comment \
  --owner OWNER \
  --repo REPO \
  --comment-id COMMENT_ID
```

## Label Operations

### Add Labels

Add labels to an issue (without removing existing labels).

```bash
python scripts/issues.py add-labels \
  --owner OWNER \
  --repo REPO \
  --number ISSUE_NUMBER \
  --labels "label1,label2"
```

### Remove Label

Remove a specific label from an issue.

```bash
python scripts/issues.py remove-label \
  --owner OWNER \
  --repo REPO \
  --number ISSUE_NUMBER \
  --label "label-name"
```

## Lock/Unlock Issue

### Lock Issue

Lock an issue to prevent further comments.

```bash
python scripts/issues.py lock \
  --owner OWNER \
  --repo REPO \
  --number ISSUE_NUMBER \
  [--reason off-topic|"too heated"|resolved|spam]
```

### Unlock Issue

Unlock a previously locked issue.

```bash
python scripts/issues.py unlock \
  --owner OWNER \
  --repo REPO \
  --number ISSUE_NUMBER
```

## Output Formats

All commands support `--format` with values:
- `json` (default) - Full JSON output
- `markdown` - Human-readable markdown
- `minimal` - Compact JSON (no whitespace)
