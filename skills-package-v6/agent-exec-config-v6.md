# Executive + Task Tracking Agent Config v6

This document is for the installation Agent. This package keeps only two business entries:

- `executive-tracking`: executive tracking
- `task-tracking`: task tracking

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

## Package Scope

Business entries:

- `executive-tracking` -> `feishu-boss-work/`
- `task-tracking` -> `feishu-exec-task-extractor/`

Shared/internal dependencies:

- `feishu-data-collector-v3/`
- `feishu-calendar-collector/`
- `feishu-task-collector/`
- `feishu-minutes-collector/`
- `feishu-group-collector/`
- `feishu-p2p-collector/`
- `feishu-mail-collector/`
- `feishu-executive-comparison/`

`feishu-user-token-registry` is intentionally not included. It must be installed first through `feishu-user-token-registry-package`, then manually configured and verified before this package is installed.

## Required Variables

Resolve these from administrator input, runtime config, or the verified setup workspace:

```text
APP_ID
APP_SECRET
AGENT_BASE_TOKEN
TABLE_ID_高管追踪报告
TABLE_ID_任务信息表
TABLE_ID_任务跟进记录表
TABLE_ID_任务巡检报告
TOKEN_BASE_TOKEN
TOKEN_TABLE_ID
BOSS_OPEN_ID
```

`TOKEN_BASE_TOKEN` and `TOKEN_TABLE_ID` point to the member token storage Bitable verified by the prerequisite package. Do not hardcode them in skill files.

## User Token Source

The token table is an external prerequisite. It must already contain:

```text
成员
应用ID
应用秘钥
授权链接
回调地址
授权码
user_access_token
refresh_token
授权状态
授权时间
过期时间
```

This package only reads the token table. It does not send authorization cards and does not create the token registry table.

## Trigger Model

```text
executive-tracking: conversation-triggered by default
task-tracking: conversation-triggered for new tasks, plus daily cron inspection
```

## AGENT_ACTION: verify_package_scope

```bash
test -f /home/gem/workspace/agent/skills/feishu-boss-work/SKILL.md
test -f /home/gem/workspace/agent/skills/feishu-exec-task-extractor/SKILL.md
test -f /home/gem/workspace/agent/skills/feishu-data-collector-v3/SKILL.md
test ! -d /home/gem/workspace/agent/skills/feishu-user-token-registry
test ! -d /home/gem/workspace/agent/skills/hire-recruit
test ! -d /home/gem/workspace/agent/skills/team-vibe-tracker
test ! -d /home/gem/workspace/agent/skills/attendance-report
test ! -d /home/gem/workspace/agent/skills/competitor-intelligence-v2
test ! -d /home/gem/workspace/agent/skills/feishu-customer-follow-tracker
```

## AGENT_ACTION: install_dependencies

```bash
python3 -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple requests
python3 - <<'PY'
import requests
print("ok: requests")
PY
```

## AGENT_ACTION: verify_credentials

```bash
lark-cli --profile {APP_ID} api POST /open-apis/auth/v3/tenant_access_token/internal \
  --data '{"app_id":"{APP_ID}","app_secret":"{APP_SECRET}"}' 2>&1 | grep -q "tenant_access_token"
```

## AGENT_ACTION: verify_permissions

```bash
lark-cli --profile {APP_ID} api GET "/open-apis/im/v1/chats?page_size=1" --as bot 2>&1 | grep -q "code.*0" && echo "ok: im"
lark-cli --profile {APP_ID} api GET "/open-apis/contact/v3/departments?page_size=1" --as bot 2>&1 | grep -q "code.*0" && echo "ok: contact"
lark-cli --profile {APP_ID} base +base-get --base-token {AGENT_BASE_TOKEN} --as bot 2>&1 | grep -q "code.*0\\|app"
```

## AGENT_ACTION: verify_existing_user_token_table

```bash
lark-cli --profile {APP_ID} base +field-list --base-token {TOKEN_BASE_TOKEN} --table-id {TOKEN_TABLE_ID} --as bot >/dev/null
```

The Agent must verify that target members have valid token rows before running tracking workflows.

## AGENT_ACTION: write_runtime_config

Write these into runtime environment or task configuration:

```text
APP_ID={APP_ID}
APP_SECRET={APP_SECRET}
AGENT_BASE_TOKEN={AGENT_BASE_TOKEN}
TABLE_ID_高管追踪报告={TABLE_ID_高管追踪报告}
TABLE_ID_任务信息表={TABLE_ID_任务信息表}
TABLE_ID_任务跟进记录表={TABLE_ID_任务跟进记录表}
TABLE_ID_任务巡检报告={TABLE_ID_任务巡检报告}
TOKEN_BASE_TOKEN={TOKEN_BASE_TOKEN}
TOKEN_TABLE_ID={TOKEN_TABLE_ID}
BOSS_OPEN_ID={BOSS_OPEN_ID}
```

## AGENT_ACTION: verify_collectors

```bash
test -x /home/gem/workspace/agent/skills/feishu-data-collector-v3/bin/feishu-data-collector-v3 || test -f /home/gem/workspace/agent/skills/feishu-data-collector-v3/bin/feishu-data-collector-v3
test -f /home/gem/workspace/agent/skills/feishu-calendar-collector/bin/feishu-calendar-collector
test -f /home/gem/workspace/agent/skills/feishu-task-collector/bin/feishu-task-collector
test -f /home/gem/workspace/agent/skills/feishu-minutes-collector/bin/feishu-minutes-collector
test -f /home/gem/workspace/agent/skills/feishu-group-collector/bin/feishu-group-collector
test -f /home/gem/workspace/agent/skills/feishu-p2p-collector/bin/feishu-p2p-collector
test -f /home/gem/workspace/agent/skills/feishu-mail-collector/bin/feishu-mail-collector
test ! -d /home/gem/workspace/agent/skills/feishu-user-token-registry
```

## AGENT_ACTION: configure_task_cron

Create a new cron job during v6 installation. Do not write a fixed job ID in this package.

Default schedule:

```yaml
schedule:
  cron: "0 21 * * *"
  tz: "Asia/Shanghai"
payload:
  kind: agentTurn
  message: |
    Run task-tracking daily inspection.
    Read unfinished tasks, collect the responsible owner's latest 7 days of Feishu data,
    judge progress/risk/overdue/completion status, update task tables, and generate inspection report.
```

After creation, record the generated values in runtime notes/config:

```text
TASK_TRACKING_CRON_JOB_ID={generated_job_id}
TASK_TRACKING_CRON="0 21 * * *"
TASK_TRACKING_CRON_TZ=Asia/Shanghai
```

## AGENT_ACTION: conversation_tests

Run:

```text
executive-tracking test: track one authorized executive and write the report table.
task-tracking test: create one small task by conversation and write task/follow-up tables.
task-tracking cron test: dry-run or manually trigger the daily inspection flow.
```

## AGENT_ACTION: final_verify

Final verification must confirm:

- Only `executive-tracking` and `task-tracking` are user-facing business entries.
- `feishu-user-token-registry` is not included in this package.
- `TOKEN_BASE_TOKEN` and `TOKEN_TABLE_ID` point to an already verified token table.
- Shared collectors exist.
- Executive tracking can write `高管追踪报告`.
- Task tracking can write `任务信息表`, `任务跟进记录表`, and `任务巡检报告`.
- Task-tracking cron was created and the generated job ID was recorded.
- Removed business skills are not installed.
