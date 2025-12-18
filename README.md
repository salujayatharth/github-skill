<div align="center">

# GitHub Skill for Claude Code

**Complete GitHub API integration with lazy-loading toolsets**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![No Dependencies](https://img.shields.io/badge/dependencies-none-brightgreen.svg)](#)
[![Claude Code](https://img.shields.io/badge/Claude-Code-blueviolet.svg)](https://claude.ai/code)
[![Token Savings](https://img.shields.io/badge/tokens-99%25_less_than_MCP-success.svg)](#token-savings-vs-github-mcp)

[Features](#features) • [Quick Start](#quick-start) • [Usage](#usage) • [Installation](#installation) • [Architecture](#architecture)

</div>

---

## Features

<table>
<tr>
<td width="50%">

### Core Capabilities

- **Repositories** — Files, branches, commits, forks
- **Issues** — Full CRUD, comments, labels, milestones
- **Pull Requests** — Create, review, merge, CI status
- **Actions** — Workflow runs, logs, triggers
- **Security** — Dependabot, code scanning, secrets
- **Search** — Repos, code, issues, users, commits

</td>
<td width="50%">

### Design Principles

- **Zero Dependencies** — Pure Python stdlib
- **Lazy Loading** — Minimal context usage
- **CLI-First** — `--help` on every command
- **Multiple Formats** — JSON, Markdown, minimal

</td>
</tr>
</table>

## Quick Start

### 1. Set Your Token

```bash
export GITHUB_TOKEN=ghp_xxxxxxxxxxxx
```

<details>
<summary><b>Token Scopes Reference</b></summary>

| Operation | Required Scopes |
|-----------|-----------------|
| Public repos | `public_repo` |
| Private repos | `repo` |
| Actions | `workflow` |
| Security | `security_events` |

</details>

### 2. Verify Authentication

```bash
python scripts/github_client.py --check-auth
```

### 3. Start Using

```bash
python scripts/issues.py list --owner octocat --repo Hello-World
```

## Usage

### Available Commands

| Script | Commands | Description |
|--------|----------|-------------|
| `repos.py` | `get-file` `list-files` `create-file` `push-files` `create-branch` `create-repo` `fork` | Repository & file operations |
| `issues.py` | `list` `get` `create` `update` `comment` `add-labels` `lock` | Issue management |
| `pull_requests.py` | `list` `get` `create` `merge` `review` `status` `request-reviewers` | Pull request workflow |
| `actions.py` | `list-runs` `get-run` `list-jobs` `get-logs` `rerun` `dispatch` `cancel` | GitHub Actions |
| `code_security.py` | `dependabot-alerts` `code-scanning-alerts` `secret-scanning-alerts` | Security alerts |
| `search.py` | `repos` `code` `issues` `users` `commits` | Search across GitHub |

### Examples

<details>
<summary><b>Create a Pull Request</b></summary>

```bash
# Create feature branch
python scripts/repos.py create-branch \
  --owner myuser --repo myrepo \
  --branch feature-x

# Create PR
python scripts/pull_requests.py create \
  --owner myuser --repo myrepo \
  --title "Add feature X" \
  --head feature-x \
  --base main \
  --body "## Changes\n- Added feature X"
```

</details>

<details>
<summary><b>Check CI Status & Merge</b></summary>

```bash
# Check status
python scripts/pull_requests.py status \
  --owner myuser --repo myrepo \
  --number 42

# Merge with squash
python scripts/pull_requests.py merge \
  --owner myuser --repo myrepo \
  --number 42 \
  --method squash
```

</details>

<details>
<summary><b>Triage Security Alerts</b></summary>

```bash
# List critical alerts
python scripts/code_security.py dependabot-alerts \
  --owner myuser --repo myrepo \
  --severity critical,high \
  --state open

# Dismiss as not used
python scripts/code_security.py update-dependabot-alert \
  --owner myuser --repo myrepo \
  --alert-number 1 \
  --state dismissed \
  --reason not_used
```

</details>

<details>
<summary><b>Trigger Workflow</b></summary>

```bash
python scripts/actions.py dispatch \
  --owner myuser --repo myrepo \
  --workflow deploy.yml \
  --ref main \
  --inputs '{"environment": "production"}'
```

</details>

<details>
<summary><b>Debug Failed CI</b></summary>

```bash
# List recent runs
python scripts/actions.py list-runs \
  --owner myuser --repo myrepo \
  --status completed

# Get job logs
python scripts/actions.py get-job-logs \
  --owner myuser --repo myrepo \
  --job-id 12345

# Rerun failed jobs
python scripts/actions.py rerun \
  --owner myuser --repo myrepo \
  --run-id 67890 \
  --failed-only
```

</details>

### Output Formats

```bash
--format json      # Default, full JSON
--format markdown  # Human-readable
--format minimal   # Compact, for piping
```

## Installation

### As Claude Code Skill

```bash
git clone https://github.com/salujayatharth/github-skill.git ~/.claude/skills/github
```

The skill auto-loads when Claude Code detects GitHub-related tasks.

### Standalone CLI

```bash
git clone https://github.com/salujayatharth/github-skill.git
cd github-skill
export GITHUB_TOKEN=ghp_xxxx
python scripts/issues.py --help
```

## Architecture

```
github-skill/
├── SKILL.md                    # Skill manifest + decision tree
├── scripts/
│   ├── github_client.py        # Core API client
│   ├── utils.py                # Shared utilities
│   ├── repos.py                # 10 commands
│   ├── issues.py               # 12 commands
│   ├── pull_requests.py        # 17 commands
│   ├── actions.py              # 15 commands
│   ├── code_security.py        # 12 commands
│   └── search.py               # 6 commands
└── references/                 # Lazy-loaded docs
    ├── repos.md
    ├── issues.md
    ├── pull-requests.md
    ├── actions.md
    ├── code-security.md
    ├── search.md
    └── api-patterns.md
```

### Progressive Disclosure

| Level | Content | Tokens | When Loaded |
|-------|---------|--------|-------------|
| 1 | Skill metadata | ~50 | Always |
| 2 | Decision tree | ~200 | Skill triggered |
| 3 | Reference docs | ~400-800 each | On-demand |

#### Token Savings vs GitHub MCP

| Approach | Tokens | vs GitHub MCP |
|----------|--------|---------------|
| [GitHub MCP](https://github.com/github/github-mcp-server) (all 91 tools) | ~46,000 | baseline |
| GitHub MCP (optimized) | ~4,600-18,400 | 60-90% less |
| **This skill** (base load) | ~250 | **99.5% less** |
| **This skill** (per operation) | ~650-1,050 | **97-98% less** |

> **Why it matters:** GitHub MCP has been described as ["a masterclass in context pollution"](https://smcleod.net/2025/08/stop-polluting-context-let-users-disable-individual-mcp-tools/) — loading 46k tokens before you even ask a question. This skill loads ~250 tokens at startup, then only the reference docs you actually need.

<details>
<summary><b>Sources</b></summary>

- [GitHub Changelog - Tool-specific configuration (Dec 2025)](https://github.blog/changelog/2025-12-10-the-github-mcp-server-adds-support-for-tool-specific-configuration-and-more/)
- [Stop Polluting Context - smcleod.net](https://smcleod.net/2025/08/stop-polluting-context-let-users-disable-individual-mcp-tools/)

</details>

## Requirements

- Python 3.7+
- No external dependencies
- GitHub Personal Access Token

## License

MIT

---

<div align="center">

**[Report Bug](https://github.com/salujayatharth/github-skill/issues)** • **[Request Feature](https://github.com/salujayatharth/github-skill/issues)**

</div>
