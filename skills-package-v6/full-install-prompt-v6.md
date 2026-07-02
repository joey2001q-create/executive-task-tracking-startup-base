# Executive Tracking + Task Tracking Install Prompt v6

You received `skills-package-v6.zip`. This is the official slim business package. It contains only two user-facing business entries:

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

This package starts at the `Agent installs skills-package-v6` step. It must not run before the token table has been verified.

## Package Boundary

`feishu-user-token-registry` is not included in this package. It is delivered separately so authorization can be installed, manually configured, and verified first.

Recruiting, team vibe, attendance, competitor intelligence, boss daily briefing, customer follow-up, finance, sales, market, and product sub-skills must not be installed or shown.

## Rules

1. Verify after every step. Continue only after verification passes.
2. Stop immediately on verification failure and report the failed step.
3. Expose only `executive-tracking` and `task-tracking` as business entries.
4. Install shared/internal collectors automatically, but do not show them as user-selectable skills.
5. Use only an already verified member token table.
6. Do not create token registry setup inside this package.
7. Do not hardcode App ID, App Secret, Base Token, Table ID, authorization URLs, user tokens, or cron job IDs.
8. Create the task-tracking cron job during v6 installation, then record the actual generated job ID in runtime notes/config.

## Step 0: Confirm Prerequisite

Ask the administrator or upstream Agent to confirm:

```text
feishu-user-token-registry was installed.
Feishu app was manually configured and published.
Member token storage Bitable exists.
Bot has management permission on the token storage Bitable.
Target members have valid user_access_token and refresh_token.
TOKEN_BASE_TOKEN and TOKEN_TABLE_ID are available to this Agent.
```

If not confirmed, stop and ask the user to finish the registry/manual setup flow first.

## Step 1: Extract

```bash
mkdir -p /home/gem/workspace/agent/skills
unzip skills-package-v6.zip -d /home/gem/workspace/agent/skills/
```

If the zip extracts an outer `skills-package-v6/` directory, move its skill directories and docs into `/home/gem/workspace/agent/skills/`.

Verify:

```bash
test -f /home/gem/workspace/agent/skills/feishu-boss-work/SKILL.md
test -f /home/gem/workspace/agent/skills/feishu-exec-task-extractor/SKILL.md
test -f /home/gem/workspace/agent/skills/feishu-data-collector-v3/SKILL.md
test -f /home/gem/workspace/agent/skills/agent-exec-config-v6.md
test ! -d /home/gem/workspace/agent/skills/feishu-user-token-registry
test ! -d /home/gem/workspace/agent/skills/hire-recruit
test ! -d /home/gem/workspace/agent/skills/team-vibe-tracker
test ! -d /home/gem/workspace/agent/skills/attendance-report
test ! -d /home/gem/workspace/agent/skills/competitor-intelligence-v2
test ! -d /home/gem/workspace/agent/skills/feishu-customer-follow-tracker
```

## Step 2: Install Python Dependency

```bash
python3 -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple requests
```

Verify:

```bash
python3 - <<'PY'
import requests
print("ok: requests")
PY
```

## Step 3: Read Execution Config

Read:

```text
/home/gem/workspace/agent/skills/agent-exec-config-v6.md
```

Execute only actions related to:

```text
verify_package_scope
install_dependencies
verify_credentials
verify_permissions
verify_existing_user_token_table
write_runtime_config
verify_collectors
configure_task_cron
final_verify
```

## Step 4: Resolve Runtime Variables

Resolve or ask for:

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

`TOKEN_BASE_TOKEN` and `TOKEN_TABLE_ID` must come from the already verified prerequisite token registry package.

Verify credentials:

```bash
lark-cli --profile {APP_ID} api POST /open-apis/auth/v3/tenant_access_token/internal \
  --data '{"app_id":"{APP_ID}","app_secret":"{APP_SECRET}"}' 2>&1 | grep -q "tenant_access_token"
```

## Step 5: Verify Existing Token Table

Do not create or install token registry here. Only verify the existing token table:

```bash
lark-cli --profile {APP_ID} base +field-list --base-token {TOKEN_BASE_TOKEN} --table-id {TOKEN_TABLE_ID} --as bot >/dev/null
```

The table must already contain:

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

At least one target member should have valid `user_access_token`, `refresh_token`, and `授权状态=有效`.

## Step 6: Verify Permissions

```bash
lark-cli --profile {APP_ID} api GET "/open-apis/im/v1/chats?page_size=1" --as bot 2>&1 | grep -q "code.*0" && echo "ok: im" || echo "fail: im"
lark-cli --profile {APP_ID} api GET "/open-apis/contact/v3/departments?page_size=1" --as bot 2>&1 | grep -q "code.*0" && echo "ok: contact" || echo "fail: contact"
```

## Step 7: Verify Business Base Tables

```bash
lark-cli --profile {APP_ID} base +field-list --base-token {AGENT_BASE_TOKEN} --table-id {TABLE_ID_高管追踪报告} --as bot >/dev/null
lark-cli --profile {APP_ID} base +field-list --base-token {AGENT_BASE_TOKEN} --table-id {TABLE_ID_任务信息表} --as bot >/dev/null
lark-cli --profile {APP_ID} base +field-list --base-token {AGENT_BASE_TOKEN} --table-id {TABLE_ID_任务跟进记录表} --as bot >/dev/null
lark-cli --profile {APP_ID} base +field-list --base-token {AGENT_BASE_TOKEN} --table-id {TABLE_ID_任务巡检报告} --as bot >/dev/null
```

## Step 8: Write Runtime Config

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

## Step 9: Verify Shared Collectors

```bash
test -f /home/gem/workspace/agent/skills/feishu-data-collector-v3/bin/feishu-data-collector-v3
test -f /home/gem/workspace/agent/skills/feishu-calendar-collector/bin/feishu-calendar-collector
test -f /home/gem/workspace/agent/skills/feishu-task-collector/bin/feishu-task-collector
test -f /home/gem/workspace/agent/skills/feishu-minutes-collector/bin/feishu-minutes-collector
test -f /home/gem/workspace/agent/skills/feishu-group-collector/bin/feishu-group-collector
test -f /home/gem/workspace/agent/skills/feishu-p2p-collector/bin/feishu-p2p-collector
test -f /home/gem/workspace/agent/skills/feishu-mail-collector/bin/feishu-mail-collector
test ! -d /home/gem/workspace/agent/skills/feishu-user-token-registry
```

## Step 10: Create Task Tracking Cron

The Agent must create a new cron job during installation. Do not assume an existing job ID.

Default daily inspection time is 21:00 Asia/Shanghai:

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

After creation, record:

```text
TASK_TRACKING_CRON_JOB_ID={generated_job_id}
TASK_TRACKING_CRON="0 21 * * *"
TASK_TRACKING_CRON_TZ=Asia/Shanghai
```

## Step 11: Conversation Tests

Run both business tests by conversation:

```text
Test executive-tracking for one authorized executive.
Test task-tracking by creating one small task and verifying it writes to the task table.
Run or dry-run the task-tracking daily inspection.
```

## Step 12: Final Verification

```bash
find /home/gem/workspace/agent/skills -maxdepth 2 -name SKILL.md | sort
```

Must include:

```text
feishu-boss-work/SKILL.md
feishu-exec-task-extractor/SKILL.md
feishu-data-collector-v3/SKILL.md
feishu-calendar-collector/SKILL.md
feishu-task-collector/SKILL.md
feishu-minutes-collector/SKILL.md
feishu-group-collector/SKILL.md
feishu-p2p-collector/SKILL.md
feishu-mail-collector/SKILL.md
feishu-executive-comparison/SKILL.md
```

Must not include:

```text
feishu-user-token-registry
hire-recruit
team-vibe-tracker
attendance-report
competitor-intelligence-v2
financial-report-analyzer-2
feishu-customer-follow-tracker
boss-daily-briefing
sales-intelligence
market-intelligence
product-intelligence
```

Final report:

```text
Installed executive-tracking and task-tracking.
The member token registry prerequisite was verified before this package.
Shared Feishu collectors are installed.
Task-tracking cron was created and its generated job ID was recorded.
No removed business skills were installed.
```
