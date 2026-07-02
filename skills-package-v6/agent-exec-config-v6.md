# Executive + Task Tracking Agent Config

> 本文档面向安装 Agent。当前包只保留两个业务入口：`executive-tracking`（高管追踪）和 `task-tracking`（任务追踪）。
> 其他招聘、考勤、竞对、老板每日简报、客户跟进等 skill 已从本包移除。

## 保留范围

### 业务入口

- `executive-tracking` -> `feishu-boss-work/`
- `task-tracking` -> `feishu-exec-task-extractor/`

### 共享依赖

两个业务入口都依赖统一数据采集层：

- `feishu-data-collector-v3/`
- `feishu-calendar-collector/`
- `feishu-task-collector/`
- `feishu-minutes-collector/`
- `feishu-group-collector/`
- `feishu-p2p-collector/`
- `feishu-mail-collector/`

高管横向对比作为高管追踪能力的一部分保留：

- `feishu-executive-comparison/`

## 安装变量

安装过程中必须解析或询问以下变量：

```text
APP_ID
APP_SECRET
INSTALL_CHAT_ID
USER_OPEN_ID
AGENT_BASE_TOKEN
TABLE_ID_高管追踪报告
TABLE_ID_任务信息表
TABLE_ID_任务跟进记录表
TABLE_ID_任务巡检报告
TOKEN_BASE_TOKEN
TOKEN_TABLE_ID
BOSS_OPEN_ID
```

## 权限范围

只申请高管追踪和任务追踪需要的权限，不再申请招聘、考勤、竞对、老板每日简报、客户跟进权限。

### Bot / Tenant Scope

```text
admin:app.info:readonly
application:application:self_manage
im:message
im:message:readonly
im:message.group_msg:get_as_user
im:message.p2p_msg:get_as_user
im:chat
im:chat:read
im:chat.members:read
im:message.reactions:read
contact:user.base:readonly
contact:contact.base:readonly
contact:user.id:readonly
contact:user.employee:readonly
contact:department.base:readonly
contact:department.organize:readonly
bitable:app
bitable:app:readonly
base:app:copy
base:block:read
base:table:read
base:table:update
base:field:read
base:record:create
base:record:update
base:record:read
base:record:retrieve
base:record:write
base:view:read
base:view:write
docx:document:create
docx:document:readonly
docx:document:write_only
drive:drive.metadata:readonly
drive:file:upload
docs:permission.member:auth
docs:permission.member:create
docs:permission.member:transfer
minutes:minutes:readonly
minutes:minutes.search:read
minutes:minutes.basic:read
minutes:minutes.transcript:export
task:tasklist:read
mail:user_mailbox.message.subject:read
mail:user_mailbox.message.body:read
mail:user_mailbox.message.address:read
offline_access
```

### User OAuth / Token 数据源

外部 token 管理流程负责把已授权用户 token 写入：

```text
TOKEN_BASE_TOKEN
TOKEN_TABLE_ID
```

本包安装流程只校验 token 表配置，不在安装过程中强制跑用户 OAuth。

## Base 表结构

本包只要求模板 Base 中存在以下表：

- `高管追踪报告`
- `任务信息表`
- `任务跟进记录表`
- `任务巡检报告`
- 用户 token 表（由 `TOKEN_BASE_TOKEN` / `TOKEN_TABLE_ID` 指向）

无需校验招聘、考勤、竞对、客户跟进、财务、销售、市场、产品等表。

## AGENT_ACTION: verify_package_scope

安装后必须确认只存在两个业务入口：

```bash
test -f /home/gem/workspace/agent/skills/feishu-boss-work/SKILL.md
test -f /home/gem/workspace/agent/skills/feishu-exec-task-extractor/SKILL.md
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

最小验证：

```bash
lark-cli --profile {APP_ID} api GET "/open-apis/im/v1/chats?page_size=1" --as bot 2>&1 | grep -q "code.*0" && echo "ok: im"
lark-cli --profile {APP_ID} api GET "/open-apis/contact/v3/departments?page_size=1" --as bot 2>&1 | grep -q "code.*0" && echo "ok: contact"
lark-cli --profile {APP_ID} base +base-get --base-token {AGENT_BASE_TOKEN} --as bot 2>&1 | grep -q "code.*0\\|app"
```

## AGENT_ACTION: write_runtime_config

在运行环境或任务配置中写入：

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
```

## AGENT_ACTION: configure_task_cron

任务追踪需要每日巡检未完成任务，默认：

```yaml
schedule:
  cron: "0 21 * * *"
  tz: "Asia/Shanghai"
payload:
  kind: agentTurn
  message: |
    运行 task-tracking 每日巡检：
    1. 读取任务信息表未完成任务
    2. 用 feishu-data-collector-v3 采集负责人近 7 天数据
    3. 判断进展、风险、逾期和完成状态
    4. 更新任务信息表并追加任务跟进记录
    5. 生成任务巡检报告并推送给老板
```

## AGENT_ACTION: final_verify

最终验证必须确认：

- 只暴露 `executive-tracking` 和 `task-tracking` 两个业务入口。
- 两个业务入口可以读取 `AGENT_BASE_TOKEN` 和对应 table id。
- `feishu-data-collector-v3` 及 6 个底层 collector 存在。
- 高管追踪可以写入 `高管追踪报告`。
- 任务追踪可以写入 `任务信息表`、`任务跟进记录表`、`任务巡检报告`。
- 未安装招聘、团队氛围、考勤、竞对、老板每日简报、客户跟进。
