# Code Security Operations

Operations for managing Dependabot alerts, code scanning alerts, and secret scanning alerts.

## Dependabot Alerts

### List Dependabot Alerts

List vulnerability alerts from Dependabot.

```bash
python scripts/code_security.py dependabot-alerts \
  --owner OWNER \
  --repo REPO \
  [--state open|dismissed|fixed] \
  [--severity critical,high,medium,low] \
  [--ecosystem npm|pip|maven|...] \
  [--package PACKAGE_NAME] \
  [--scope development|runtime] \
  [--sort created|updated] \
  [--direction asc|desc] \
  [--per-page 30]
```

**Examples**:
```bash
# List critical and high severity alerts
python scripts/code_security.py dependabot-alerts --owner myuser --repo myrepo --severity critical,high

# List open alerts for npm packages
python scripts/code_security.py dependabot-alerts --owner myuser --repo myrepo --state open --ecosystem npm
```

**Returns**: List of alerts with severity, affected package, advisory details, and remediation info.

### Get Single Alert

Get full details of a Dependabot alert.

```bash
python scripts/code_security.py get-dependabot-alert \
  --owner OWNER \
  --repo REPO \
  --alert-number ALERT_NUMBER
```

### Update Alert (Dismiss/Reopen)

Dismiss or reopen a Dependabot alert.

```bash
python scripts/code_security.py update-dependabot-alert \
  --owner OWNER \
  --repo REPO \
  --alert-number ALERT_NUMBER \
  --state dismissed|open \
  [--reason fix_started|inaccurate|no_bandwidth|not_used|tolerable_risk] \
  [--comment "Dismissal reason"]
```

**Examples**:
```bash
# Dismiss as not used
python scripts/code_security.py update-dependabot-alert \
  --owner myuser --repo myrepo --alert-number 1 \
  --state dismissed --reason not_used \
  --comment "This package is only used in tests"

# Reopen dismissed alert
python scripts/code_security.py update-dependabot-alert \
  --owner myuser --repo myrepo --alert-number 1 \
  --state open
```

## Code Scanning Alerts

### List Code Scanning Alerts

List alerts from code scanning (CodeQL, etc.).

```bash
python scripts/code_security.py code-scanning-alerts \
  --owner OWNER \
  --repo REPO \
  [--state open|closed|dismissed|fixed] \
  [--severity critical,high,medium,low,warning,note,error] \
  [--tool-name codeql|...] \
  [--ref BRANCH] \
  [--sort created|updated] \
  [--per-page 30]
```

**Examples**:
```bash
# List open critical alerts
python scripts/code_security.py code-scanning-alerts --owner myuser --repo myrepo --state open --severity critical

# List alerts from CodeQL
python scripts/code_security.py code-scanning-alerts --owner myuser --repo myrepo --tool-name codeql
```

### Get Single Alert

```bash
python scripts/code_security.py get-code-scanning-alert \
  --owner OWNER \
  --repo REPO \
  --alert-number ALERT_NUMBER
```

### Update Alert

Dismiss or reopen a code scanning alert.

```bash
python scripts/code_security.py update-code-scanning-alert \
  --owner OWNER \
  --repo REPO \
  --alert-number ALERT_NUMBER \
  --state dismissed|open \
  [--reason "false positive"|"won't fix"|"used in tests"] \
  [--comment "Reason for dismissal"]
```

### List Analyses

List code scanning analysis runs.

```bash
python scripts/code_security.py code-scanning-analyses \
  --owner OWNER \
  --repo REPO \
  [--ref BRANCH] \
  [--tool-name codeql]
```

## Secret Scanning Alerts

### List Secret Scanning Alerts

List detected secrets in the repository.

```bash
python scripts/code_security.py secret-scanning-alerts \
  --owner OWNER \
  --repo REPO \
  [--state open|resolved] \
  [--secret-type SECRET_TYPE] \
  [--resolution RESOLUTION] \
  [--sort created|updated] \
  [--per-page 30]
```

### Get Single Alert

```bash
python scripts/code_security.py get-secret-scanning-alert \
  --owner OWNER \
  --repo REPO \
  --alert-number ALERT_NUMBER
```

### Update Alert

Resolve or reopen a secret scanning alert.

```bash
python scripts/code_security.py update-secret-scanning-alert \
  --owner OWNER \
  --repo REPO \
  --alert-number ALERT_NUMBER \
  --state resolved|open \
  [--resolution false_positive|wont_fix|revoked|used_in_tests|pattern_deleted|pattern_edited] \
  [--comment "Resolution details"]
```

### List Secret Locations

See where a detected secret appears in the repository.

```bash
python scripts/code_security.py secret-scanning-locations \
  --owner OWNER \
  --repo REPO \
  --alert-number ALERT_NUMBER
```

## Security Advisories

List repository security advisories.

```bash
python scripts/code_security.py security-advisories \
  --owner OWNER \
  --repo REPO
```

## Common Workflows

### Security Triage Workflow

```bash
# 1. List critical Dependabot alerts
python scripts/code_security.py dependabot-alerts --owner myuser --repo myrepo --severity critical --state open

# 2. Review each alert
python scripts/code_security.py get-dependabot-alert --owner myuser --repo myrepo --alert-number 1

# 3. Dismiss if not applicable
python scripts/code_security.py update-dependabot-alert \
  --owner myuser --repo myrepo --alert-number 1 \
  --state dismissed --reason not_used

# 4. Check code scanning alerts
python scripts/code_security.py code-scanning-alerts --owner myuser --repo myrepo --state open

# 5. Check for exposed secrets
python scripts/code_security.py secret-scanning-alerts --owner myuser --repo myrepo --state open
```

## Required Token Scopes

- `security_events` - Required for code scanning and secret scanning
- `repo` - Required for Dependabot alerts (or `security_events` for public repos)

**Note**: Some security features require GitHub Advanced Security license for private repositories.

## Output Formats

All commands support `--format` with values:
- `json` (default) - Full JSON output
- `markdown` - Human-readable markdown
- `minimal` - Compact JSON (no whitespace)
