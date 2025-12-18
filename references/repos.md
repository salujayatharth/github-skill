# Repository Operations

Operations for managing repository files, branches, and repository settings.

## Get File Contents

Retrieve file or directory contents from a repository.

```bash
python scripts/repos.py get-file \
  --owner OWNER \
  --repo REPO \
  --path PATH \
  [--branch BRANCH]
```

**Returns**: File content with `decoded_content` field containing the text, or directory listing as array.

**Example**:
```bash
python scripts/repos.py get-file --owner octocat --repo Hello-World --path README.md
```

## List Repository Files

List files in a directory.

```bash
python scripts/repos.py list-files \
  --owner OWNER \
  --repo REPO \
  [--path PATH] \
  [--branch BRANCH]
```

**Example**:
```bash
python scripts/repos.py list-files --owner octocat --repo Hello-World --path src
```

## Get Repository Details

Get repository metadata (description, stars, forks, default branch, etc).

```bash
python scripts/repos.py get \
  --owner OWNER \
  --repo REPO
```

## Create or Update File

Create a new file or update existing file with a commit.

```bash
python scripts/repos.py create-file \
  --owner OWNER \
  --repo REPO \
  --path PATH \
  --content "FILE_CONTENT" \
  --message "Commit message" \
  [--branch BRANCH] \
  [--sha SHA]
```

**Note**: For updates, you must provide the current file's SHA (from `get-file` response).

**Example - Create new file**:
```bash
python scripts/repos.py create-file \
  --owner myuser --repo myrepo \
  --path docs/guide.md \
  --content "# Guide\n\nWelcome!" \
  --message "Add documentation guide"
```

**Example - Update existing file**:
```bash
# First get the current SHA
python scripts/repos.py get-file --owner myuser --repo myrepo --path README.md
# Then update with that SHA
python scripts/repos.py create-file \
  --owner myuser --repo myrepo \
  --path README.md \
  --content "# Updated README" \
  --message "Update README" \
  --sha abc123def456
```

## Push Multiple Files

Commit multiple files in a single commit using the Git Data API.

```bash
python scripts/repos.py push-files \
  --owner OWNER \
  --repo REPO \
  --branch BRANCH \
  --message "Commit message" \
  --files '{"path/to/file1.txt": "content1", "path/to/file2.txt": "content2"}'
```

**Example**:
```bash
python scripts/repos.py push-files \
  --owner myuser --repo myrepo \
  --branch main \
  --message "Add multiple config files" \
  --files '{"config/app.json": "{\"version\": 1}", "config/db.json": "{\"host\": \"localhost\"}"}'
```

## Delete File

Delete a file from the repository.

```bash
python scripts/repos.py delete-file \
  --owner OWNER \
  --repo REPO \
  --path PATH \
  --message "Commit message" \
  --sha SHA \
  [--branch BRANCH]
```

## Create Branch

Create a new branch from an existing branch.

```bash
python scripts/repos.py create-branch \
  --owner OWNER \
  --repo REPO \
  --branch NEW_BRANCH \
  [--from-branch SOURCE_BRANCH]
```

**Example**:
```bash
python scripts/repos.py create-branch \
  --owner myuser --repo myrepo \
  --branch feature-login \
  --from-branch main
```

## List Branches

List all branches in a repository.

```bash
python scripts/repos.py list-branches \
  --owner OWNER \
  --repo REPO \
  [--per-page 30] \
  [--page 1]
```

## Create Repository

Create a new repository for the authenticated user.

```bash
python scripts/repos.py create-repo \
  --name REPO_NAME \
  [--description "Description"] \
  [--private] \
  [--auto-init]
```

**Example**:
```bash
python scripts/repos.py create-repo \
  --name my-awesome-project \
  --description "A fantastic new project" \
  --private \
  --auto-init
```

## Fork Repository

Fork a repository to your account or an organization.

```bash
python scripts/repos.py fork \
  --owner OWNER \
  --repo REPO \
  [--organization ORG]
```

**Example**:
```bash
python scripts/repos.py fork --owner facebook --repo react
```

## Output Formats

All commands support `--format` with values:
- `json` (default) - Full JSON output
- `markdown` - Human-readable markdown
- `minimal` - Compact JSON (no whitespace)
