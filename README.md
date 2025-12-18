# GitHub Skill for Claude Code

A Claude Code skill that provides complete GitHub API integration with lazy-loading toolsets. Replicates GitHub MCP functionality using pure Python (no dependencies).

## Features

- **Full GitHub API Coverage** — Repositories, Issues, Pull Requests, Actions, Security, Search
- **Lazy Loading** — Toolset documentation loads on-demand to minimize context usage
- **Zero Dependencies** — Pure Python stdlib, works anywhere with Python 3
- **CLI-First Design** — All scripts support `--help` and multiple output formats

## Quick Start

### 1. Set Your Token

```bash
export GITHUB_TOKEN=ghp_xxxxxxxxxxxx
```

Required scopes depend on operations:
| Operation | Scopes |
|-----------|--------|
| Public repos | `public_repo` |
| Private repos | `repo` |
| Actions | `workflow` |
| Security | `security_events` |

### 2. Verify Authentication

```bash
python scripts/github_client.py --check-auth
```

### 3. Start Using

```bash
# List issues
python scripts/issues.py list --owner octocat --repo Hello-World

# Get file contents
python scripts/repos.py get-file --owner octocat --repo Hello-World --path README.md

# Search code
python scripts/search.py code --query "def main repo:owner/repo"
```

## Available Operations

| Script | Operations |
|--------|------------|
| `repos.py` | Get/create files, branches, fork, create repos |
| `issues.py` | List, create, update, comment, labels, lock |
| `pull_requests.py` | Create, review, merge, check status, request reviewers |
| `actions.py` | List runs, view logs, rerun, trigger workflows |
| `code_security.py` | Dependabot, code scanning, secret scanning |
| `search.py` | Search repos, code, issues, users, commits |

## Usage Examples

### Create a Pull Request

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
  --base main
```

### Check CI Status

```bash
python scripts/pull_requests.py status \
  --owner myuser --repo myrepo \
  --number 42
```

### Triage Security Alerts

```bash
# List critical Dependabot alerts
python scripts/code_security.py dependabot-alerts \
  --owner myuser --repo myrepo \
  --severity critical,high \
  --state open
```

### Trigger Workflow

```bash
python scripts/actions.py dispatch \
  --owner myuser --repo myrepo \
  --workflow deploy.yml \
  --ref main \
  --inputs '{"environment": "production"}'
```

## Output Formats

All scripts support `--format`:

```bash
# JSON (default) - for programmatic use
python scripts/issues.py list --owner octocat --repo Hello-World --format json

# Markdown - human readable
python scripts/issues.py list --owner octocat --repo Hello-World --format markdown

# Minimal - compact JSON for piping
python scripts/issues.py list --owner octocat --repo Hello-World --format minimal
```

## Project Structure

```
github-skill/
├── SKILL.md                 # Skill manifest with decision tree
├── scripts/
│   ├── github_client.py     # Core API client
│   ├── utils.py             # Shared utilities
│   ├── repos.py             # Repository operations
│   ├── issues.py            # Issue management
│   ├── pull_requests.py     # PR operations
│   ├── actions.py           # GitHub Actions
│   ├── code_security.py     # Security alerts
│   └── search.py            # Search operations
└── references/              # Lazy-loaded documentation
    ├── repos.md
    ├── issues.md
    ├── pull-requests.md
    ├── actions.md
    ├── code-security.md
    ├── search.md
    └── api-patterns.md
```

## Installing as Claude Code Skill

Copy to your Claude Code skills directory:

```bash
cp -r github-skill ~/.claude/skills/github
```

The skill will be available in Claude Code with lazy-loading — only the relevant reference files load when needed.

## Architecture

### Three-Level Progressive Disclosure

1. **Level 1 — Metadata** (~50 tokens): Skill name and description in SKILL.md frontmatter
2. **Level 2 — Decision Tree** (~200 tokens): SKILL.md body with operation routing
3. **Level 3 — References** (on-demand): Individual `references/*.md` files loaded when specific operations are needed

This architecture minimizes context window usage while providing comprehensive GitHub functionality.

## Requirements

- Python 3.7+
- No external dependencies (uses only stdlib)
- GitHub Personal Access Token

## License

MIT
