# Skills Package v6

This is the slim business package for executive tracking and task tracking.

## Prerequisite

Before installing this package, install and verify the standalone prerequisite package:

```text
feishu-user-token-registry-package
```

That prerequisite package is responsible for Feishu member OAuth authorization and token table verification. This v6 package only consumes an already verified member token table through placeholders:

```text
TOKEN_BASE_TOKEN={TOKEN_BASE_TOKEN}
TOKEN_TABLE_ID={TOKEN_TABLE_ID}
```

Do not install `feishu-user-token-registry` from this package. It is delivered separately so authorization can be validated first.

## Business Entries

- `executive-tracking`: executive tracking, implemented by `feishu-boss-work/`
- `task-tracking`: task tracking, implemented by `feishu-exec-task-extractor/`

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
