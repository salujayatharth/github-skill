# Common API Patterns & Troubleshooting

Reference for error handling, rate limiting, and common workflow patterns.

## Authentication

All scripts require `GITHUB_TOKEN` environment variable:

```bash
export GITHUB_TOKEN=ghp_xxxxxxxxxxxx
```

**Verify authentication**:
```bash
python scripts/github_client.py --check-auth
```

## Error Handling

### 401 Unauthorized

**Cause**: Invalid or expired token.

**Solutions**:
- Verify `GITHUB_TOKEN` is set: `echo $GITHUB_TOKEN`
- Check token is valid and not expired
- Regenerate token at https://github.com/settings/tokens

### 403 Forbidden

**Causes**:
- Token lacks required scopes
- Rate limit exceeded
- Resource requires specific permissions

**Solutions**:
- Check rate limit: `python scripts/github_client.py --rate-limit`
- Add required scopes to token
- For organization resources, ensure token has org access

### 404 Not Found

**Causes**:
- Repository/resource doesn't exist
- Token doesn't have access to private repo
- Typo in owner/repo name

**Solutions**:
- Verify repository exists and name is correct
- Ensure token has `repo` scope for private repositories
- Check organization membership if applicable

### 422 Unprocessable Entity

**Cause**: Validation failed on request data.

**Common issues**:
- Missing required fields
- Invalid field values
- Conflicting parameters

**Solutions**:
- Check the error message for specific field
- Verify all required parameters are provided
- Check parameter format matches API expectations

## Rate Limiting

**Check current limits**:
```bash
python scripts/github_client.py --rate-limit
```

**Rate limits**:
| API Type | Limit | Notes |
|----------|-------|-------|
| Core API | 5,000/hour | Authenticated requests |
| Search API | 30/minute | More restrictive |
| Code Search | 10/minute | Most restrictive |

**When rate limited**:
- Wait for reset (shown in rate-limit output)
- Use conditional requests where possible
- Batch operations to reduce API calls

## Pagination

All list operations support pagination:

```bash
python scripts/issues.py list --owner myuser --repo myrepo --per-page 100 --page 1
```

**Parameters**:
- `--per-page N` - Results per page (max 100)
- `--page N` - Page number (1-indexed)

**Getting all results**: Increment `--page` until empty response.

## Common Workflow Patterns

### PR Workflow

```bash
# 1. Create a feature branch
python scripts/repos.py create-branch --owner myuser --repo myrepo --branch feature-x

# 2. Push changes (using git or push-files for small changes)
python scripts/repos.py push-files \
  --owner myuser --repo myrepo \
  --branch feature-x \
  --message "Add new feature" \
  --files '{"src/feature.py": "# New feature code"}'

# 3. Create pull request
python scripts/pull_requests.py create \
  --owner myuser --repo myrepo \
  --title "Add feature X" \
  --head feature-x \
  --base main \
  --body "## Summary\n- Added feature X\n\n## Testing\n- Unit tests added"

# 4. Check CI status
python scripts/pull_requests.py status --owner myuser --repo myrepo --number 42

# 5. Merge when ready
python scripts/pull_requests.py merge --owner myuser --repo myrepo --number 42 --method squash
```

### Issue Triage Workflow

```bash
# 1. List open bugs
python scripts/issues.py list --owner myuser --repo myrepo --state open --labels bug

# 2. Assign and label
python scripts/issues.py update --owner myuser --repo myrepo --number 1 \
  --assignees developer1 --labels "bug,in-progress"

# 3. Add progress comment
python scripts/issues.py comment --owner myuser --repo myrepo --number 1 \
  --body "Investigating this issue. Initial analysis: ..."

# 4. Close when fixed
python scripts/issues.py update --owner myuser --repo myrepo --number 1 \
  --state closed --state-reason completed
```

### CI Debugging Workflow

```bash
# 1. List recent failed runs
python scripts/actions.py list-runs --owner myuser --repo myrepo --status completed

# 2. Get run details
python scripts/actions.py get-run --owner myuser --repo myrepo --run-id 12345

# 3. List jobs to find failures
python scripts/actions.py list-jobs --owner myuser --repo myrepo --run-id 12345

# 4. Get logs for failed job
python scripts/actions.py get-job-logs --owner myuser --repo myrepo --job-id 67890

# 5. After fixing, rerun failed jobs
python scripts/actions.py rerun --owner myuser --repo myrepo --run-id 12345 --failed-only
```

### Security Review Workflow

```bash
# 1. Check Dependabot alerts
python scripts/code_security.py dependabot-alerts \
  --owner myuser --repo myrepo \
  --state open --severity critical,high

# 2. Review specific alert
python scripts/code_security.py get-dependabot-alert \
  --owner myuser --repo myrepo --alert-number 1

# 3. Dismiss if not applicable
python scripts/code_security.py update-dependabot-alert \
  --owner myuser --repo myrepo --alert-number 1 \
  --state dismissed --reason not_used

# 4. Check for exposed secrets
python scripts/code_security.py secret-scanning-alerts \
  --owner myuser --repo myrepo --state open
```

### Cross-Repository Search

```bash
# Find implementations across repos
python scripts/search.py code --query "def authenticate org:myorg language:python"

# Find related issues
python scripts/search.py issues --query "authentication bug org:myorg is:open"

# Find active maintainers
python scripts/search.py users --query "org:myorg type:user" --sort repositories
```

## Tips

### Efficient API Usage

1. **Use specific endpoints**: Get a single issue instead of listing all
2. **Filter server-side**: Use query parameters instead of client filtering
3. **Limit fields when possible**: Some endpoints support field selection
4. **Cache when appropriate**: Repeated reads can use cached data

### Script Patterns

1. **Always check --help first**: `python scripts/repos.py get-file --help`
2. **Use --format markdown for reading**: Easier to scan than JSON
3. **Use --format minimal for piping**: Compact for processing
4. **Combine with jq for filtering**: `python scripts/... | jq '.items[].name'`

### Safety

1. **Verify before destructive operations**: Check state before delete/close
2. **Use --sha for updates**: Prevents race conditions on file updates
3. **Check mergeable status**: Before attempting PR merge
4. **Review alert details**: Before dismissing security alerts
