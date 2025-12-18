# Search Operations

Search across GitHub repositories, code, issues, users, and commits.

## Search Repositories

```bash
python scripts/search.py repos \
  --query "SEARCH_QUERY" \
  [--sort stars|forks|help-wanted-issues|updated] \
  [--order asc|desc] \
  [--per-page 30]
```

**Query syntax examples**:
- `language:python stars:>1000` - Python repos with 1000+ stars
- `user:octocat` - Repos owned by octocat
- `org:github` - Repos in GitHub org
- `topic:machine-learning` - Repos with ML topic
- `fork:true` - Include forks in results
- `archived:false` - Exclude archived repos

**Examples**:
```bash
# Popular Python repos
python scripts/search.py repos --query "language:python stars:>5000" --sort stars

# React component libraries
python scripts/search.py repos --query "topic:react-components stars:>100"
```

## Search Code

Search code across repositories. Requires authentication.

```bash
python scripts/search.py code \
  --query "SEARCH_QUERY" \
  [--sort indexed] \
  [--order asc|desc] \
  [--per-page 30]
```

**Query syntax examples**:
- `addClass in:file language:javascript` - Search in JavaScript files
- `repo:owner/repo path:src extension:py` - Search in specific repo and path
- `filename:config.yml` - Search by filename
- `org:github extension:rb` - Search Ruby files in GitHub org

**Examples**:
```bash
# Find API endpoint definitions
python scripts/search.py code --query "app.get repo:expressjs/express extension:js"

# Find configuration files
python scripts/search.py code --query "filename:tsconfig.json org:microsoft"
```

**Note**: Code search has stricter rate limits (30 requests/minute).

## Search Issues and Pull Requests

```bash
python scripts/search.py issues \
  --query "SEARCH_QUERY" \
  [--sort comments|reactions|created|updated|interactions] \
  [--order asc|desc] \
  [--per-page 30]
```

**Query syntax examples**:
- `repo:owner/repo is:open is:issue label:bug` - Open bugs in repo
- `author:username is:pr is:merged` - User's merged PRs
- `mentions:username` - Issues mentioning user
- `assignee:username is:open` - Open issues assigned to user
- `org:github type:pr is:open` - Open PRs in GitHub org
- `label:"good first issue" language:python` - Good first issues

**Examples**:
```bash
# Find bugs to work on
python scripts/search.py issues --query "repo:facebook/react is:open label:bug label:\"good first issue\""

# Find your open PRs
python scripts/search.py issues --query "is:pr is:open author:@me"

# Find recently updated issues
python scripts/search.py issues --query "repo:owner/repo is:issue" --sort updated
```

## Search Users

```bash
python scripts/search.py users \
  --query "SEARCH_QUERY" \
  [--sort followers|repositories|joined] \
  [--order asc|desc] \
  [--per-page 30]
```

**Query syntax examples**:
- `fullname:John location:USA` - Users named John in USA
- `type:user followers:>1000` - Users with 1000+ followers
- `language:python` - Users who write Python
- `type:org` - Search organizations

**Examples**:
```bash
# Find prolific Python developers
python scripts/search.py users --query "language:python followers:>500" --sort followers

# Find organizations
python scripts/search.py users --query "type:org machine learning"
```

## Search Commits

```bash
python scripts/search.py commits \
  --query "SEARCH_QUERY" \
  [--sort author-date|committer-date] \
  [--order asc|desc] \
  [--per-page 30]
```

**Query syntax examples**:
- `repo:owner/repo fix bug` - Commits mentioning "fix bug"
- `author:username committer-date:>2024-01-01` - User's commits after date
- `org:github merge` - Merge commits in GitHub org

**Examples**:
```bash
# Find recent bug fixes
python scripts/search.py commits --query "repo:owner/repo fix" --sort committer-date

# Find commits by author
python scripts/search.py commits --query "author:octocat repo:octocat/Hello-World"
```

## Search Topics

```bash
python scripts/search.py topics \
  --query "SEARCH_QUERY" \
  [--per-page 30]
```

**Examples**:
```bash
python scripts/search.py topics --query "machine-learning"
python scripts/search.py topics --query "javascript framework"
```

## Query Syntax Reference

### Common Qualifiers

| Qualifier | Example | Description |
|-----------|---------|-------------|
| `in:` | `in:file`, `in:path`, `in:name` | Where to search |
| `user:` | `user:octocat` | Filter by user |
| `org:` | `org:github` | Filter by organization |
| `repo:` | `repo:owner/repo` | Filter by repository |
| `language:` | `language:python` | Filter by language |

### Repository Qualifiers

| Qualifier | Example | Description |
|-----------|---------|-------------|
| `stars:` | `stars:>1000`, `stars:100..500` | Filter by stars |
| `forks:` | `forks:>100` | Filter by forks |
| `size:` | `size:>1000` | Filter by size (KB) |
| `pushed:` | `pushed:>2024-01-01` | Filter by last push |
| `created:` | `created:<2020-01-01` | Filter by creation date |
| `topic:` | `topic:react` | Filter by topic |
| `archived:` | `archived:false` | Include/exclude archived |
| `is:` | `is:public`, `is:private` | Filter by visibility |

### Issue/PR Qualifiers

| Qualifier | Example | Description |
|-----------|---------|-------------|
| `is:` | `is:open`, `is:closed`, `is:merged` | Filter by state |
| `type:` | `type:issue`, `type:pr` | Filter by type |
| `author:` | `author:username` | Filter by author |
| `assignee:` | `assignee:username` | Filter by assignee |
| `mentions:` | `mentions:username` | Filter by mentions |
| `label:` | `label:bug` | Filter by label |
| `milestone:` | `milestone:"v1.0"` | Filter by milestone |
| `no:` | `no:label`, `no:assignee` | Filter by missing |

### Date Qualifiers

| Format | Example | Description |
|--------|---------|-------------|
| `>YYYY-MM-DD` | `created:>2024-01-01` | After date |
| `<YYYY-MM-DD` | `pushed:<2023-01-01` | Before date |
| `YYYY-MM-DD..YYYY-MM-DD` | `created:2024-01-01..2024-06-01` | Date range |

## Output Formats

All commands support `--format` with values:
- `json` (default) - Full JSON output
- `markdown` - Human-readable markdown
- `minimal` - Compact JSON (no whitespace)

## Rate Limits

- Standard search: 30 requests/minute
- Code search: 10 requests/minute
- Authenticated requests have higher limits
