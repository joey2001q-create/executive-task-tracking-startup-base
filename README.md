# Executive Task Tracking Startup Base

This repository packages a two-stage startup base for Feishu executive tracking and task tracking.

## Correct Test Flow

```text
Agent installs registry
-> Administrator manually configures Feishu app and Bitable
-> Administrator says "send an authorization card to XX"
-> Agent sends the authorization card
-> Member authorizes and token is written to Bitable
-> Agent verifies the token table
-> Agent installs skills-package-v6
-> Agent creates the task-tracking cron job
-> Administrator tests executive-tracking and task-tracking by conversation
```

## Download These Two Packages

Use these two zip packages for testing:

```text
feishu-user-token-registry-package.zip
skills-package-v6.zip
```

Install and verify them in that order.

## Package Roles

- `feishu-user-token-registry-package/`: prerequisite authorization package. It can be installed first, then waits for the administrator to manually configure Feishu app permissions, callback URL, token Bitable, bot permissions, and app publishing.
- `skills-package-v6/`: official slim business package. It exposes only executive tracking and task tracking, reads the already verified token table, and creates the task-tracking daily cron during installation.

## Business Scope

Only these two business entries are exposed:

- `executive-tracking`
- `task-tracking`

The following old business skills are intentionally excluded:

- recruiting
- team vibe
- attendance
- competitor intelligence
- boss daily briefing
- customer follow-up
- finance/sales/market/product sub-skills

## Safety Rules

- Do not commit real App IDs, App Secrets, Base Tokens, Table IDs, authorization codes, user tokens, or refresh tokens.
- Do not write fixed cron job IDs into the package. The Agent records the actual generated job ID during installation.
- Do not commit macOS metadata or temporary extraction directories.
