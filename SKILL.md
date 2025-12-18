---
name: github
description: >-
  Complete GitHub integration for repositories, issues, PRs, workflows, and security.
  Use when working with GitHub: (1) Repository operations - get/create files, branches, search code,
  (2) Issue management - list, create, update, comment on issues,
  (3) Pull requests - create, review, merge PRs, check CI status,
  (4) GitHub Actions - list workflows, view runs, download logs, trigger workflows,
  (5) Code security - Dependabot alerts, code scanning, secret scanning.
  Requires GITHUB_TOKEN environment variable with appropriate scopes.
allowed-tools:
  - Bash
  - Read
---

# GitHub Integration

Complete GitHub API integration for Claude Code. All operations require the `GITHUB_TOKEN` environment variable.

## Quick Start

**Verify authentication**:
```bash
python scripts/github_client.py --check-auth
```

**Check rate limits**:
```bash
python scripts/github_client.py --rate-limit
```

## Operation Reference

Choose your operation and load the appropriate reference file for detailed usage.

| Task | Reference File | Common Operations |
|------|----------------|-------------------|
| **Repository/Files** | [repos.md](references/repos.md) | Get files, create/update files, branches, fork |
| **Issues** | [issues.md](references/issues.md) | List, create, update, comment, labels |
| **Pull Requests** | [pull-requests.md](references/pull-requests.md) | Create, review, merge, check status |
| **GitHub Actions** | [actions.md](references/actions.md) | List runs, view logs, rerun, trigger |
| **Security** | [code-security.md](references/code-security.md) | Dependabot, code scanning, secrets |
| **Search** | [search.md](references/search.md) | Search repos, code, issues, users |
| **Troubleshooting** | [api-patterns.md](references/api-patterns.md) | Error handling, rate limits, patterns |

## Decision Tree

```
What do you need to do?
│
├── Work with files or code?
│   └── Read references/repos.md
│       - Get file contents
│       - Create/update files
│       - Create branches
│       - Fork repositories
│
├── Manage issues?
│   └── Read references/issues.md
│       - List/filter issues
│       - Create issues
│       - Update status/labels
│       - Add comments
│
├── Work with pull requests?
│   └── Read references/pull-requests.md
│       - Create PRs
│       - Review/approve
│       - Check CI status
│       - Merge PRs
│
├── GitHub Actions / CI?
│   └── Read references/actions.md
│       - List workflow runs
│       - View/download logs
│       - Rerun failed jobs
│       - Trigger workflows
│
├── Security alerts?
│   └── Read references/code-security.md
│       - Dependabot alerts
│       - Code scanning
│       - Secret scanning
│
└── Search GitHub?
    └── Read references/search.md
        - Search repositories
        - Search code
        - Search issues/PRs
        - Search users
```

## All Scripts Support --help

Run any script with `--help` to see full usage:

```bash
python scripts/repos.py --help
python scripts/issues.py --help
python scripts/pull_requests.py --help
python scripts/search.py --help
python scripts/actions.py --help
python scripts/code_security.py --help
```

## Output Formats

All scripts support `--format`:
- `json` (default) - Full JSON output
- `markdown` - Human-readable format
- `minimal` - Compact JSON

## Required Token Scopes

| Operation | Required Scopes |
|-----------|-----------------|
| Repositories (public) | `public_repo` |
| Repositories (private) | `repo` |
| Issues & PRs | `repo` |
| GitHub Actions | `workflow` |
| Code Security | `security_events` |
| Search Code | Authentication required |
