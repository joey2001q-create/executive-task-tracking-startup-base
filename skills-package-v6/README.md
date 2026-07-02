# Skills Package v6

This is the slim business package for executive tracking and task tracking.

## Correct End-To-End Flow

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

## Prerequisite

Before installing this package, the standalone prerequisite package must already be installed, manually configured, and verified:

```text
feishu-user-token-registry-package
```

That prerequisite package is responsible for Feishu member OAuth authorization and token table verification. This v6 package only consumes an already verified member token table through runtime placeholders:

```text
TOKEN_BASE_TOKEN={TOKEN_BASE_TOKEN}
TOKEN_TABLE_ID={TOKEN_TABLE_ID}
```

Do not install `feishu-user-token-registry` from this package.

## Business Entries

- `executive-tracking`: executive tracking, implemented by `feishu-boss-work/`
- `task-tracking`: task tracking, implemented by `feishu-exec-task-extractor/`

## Trigger Model

- `executive-tracking`: conversation-triggered by default.
- `task-tracking`: conversation-triggered for new tasks, plus a daily 21:00 Asia/Shanghai cron inspection created by the Agent during v6 installation.

The cron job ID is generated at install time. Do not write a fixed cron job ID into this package.

## Shared/Internal Dependencies

These directories are runtime dependencies for the two business entries. They are internal components, not user-selectable business skills:

- `feishu-data-collector-v3/`
- `feishu-calendar-collector/`
- `feishu-task-collector/`
- `feishu-minutes-collector/`
- `feishu-group-collector/`
- `feishu-p2p-collector/`
- `feishu-mail-collector/`
- `feishu-executive-comparison/`

## Install Entry

After giving `skills-package-v6.zip` to the Agent, ask it to read and execute:

```text
full-install-prompt-v6.md
```

Only two business entries should be exposed to users: executive tracking and task tracking.
