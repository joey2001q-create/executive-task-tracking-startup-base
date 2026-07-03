# 高管追踪 + 任务追踪 Agent 执行配置 v6

本文件面向安装 Agent。v6 只保留两个业务入口：

- `executive-tracking`：高管追踪，对应 `feishu-boss-work/`
- `task-tracking`：任务追踪，对应 `feishu-exec-task-extractor/`

`feishu-user-token-registry` 不在本包内。前置授权包完成后，本包负责自动创建业务 Base、按 v5 字段清单创建业务表，并自动解析业务表 ID。

## 运行变量来源

安装开始时从已绑定的飞书应用 profile、应用运行时安全配置、前置 registry 运行时记录或 Token 表配置行读取：

```text
APP_ID
APP_SECRET
TOKEN_BASE_TOKEN
TOKEN_TABLE_ID
```

`APP_SECRET` 是应用侧安全凭证，不要在聊天里向管理员索要或要求粘贴。读取不到时停止安装，提示管理员先完成飞书应用绑定或运行时凭证配置。

安装过程中必须由 Agent 自动生成/解析，不要向管理员索要：

```text
AGENT_BASE_TOKEN
TABLE_ID_高管追踪报告
TABLE_ID_任务信息表
TABLE_ID_任务跟进记录表
TABLE_ID_任务巡检报告
```

`BOSS_OPEN_ID` 优先从当前对话用户或已授权管理员记录解析；解析不到时只问一次。

## 业务 Base 与字段规则

```text
业务 Base 名称：高管追踪与任务追踪数据中枢
创建方式：Agent 自动创建
字段来源：v5 原字段定义
```

创建后在新 Base 中解析这些表：

```text
高管追踪报告
任务信息表
任务跟进记录表
任务巡检报告
```

v5 字段结构不可变。不得主观新增、删减、改名或改类型。

## AGENT_ACTION: verify_package_scope

```bash
test -f /home/gem/workspace/agent/skills/feishu-boss-work/SKILL.md
test -f /home/gem/workspace/agent/skills/feishu-exec-task-extractor/SKILL.md
test -f /home/gem/workspace/agent/skills/feishu-data-collector-v3/SKILL.md
test -f /home/gem/workspace/agent/skills/feishu-executive-comparison/SKILL.md
test ! -d /home/gem/workspace/agent/skills/feishu-user-token-registry
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

## AGENT_ACTION: verify_registry_token_table

```bash
lark-cli --profile {APP_ID} base +field-list --base-token {TOKEN_BASE_TOKEN} --table-id {TOKEN_TABLE_ID} --as bot >/dev/null
```

必须验证 Token 表字段：

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

至少一名目标成员必须有有效 `user_access_token` 和 `refresh_token`。

## AGENT_ACTION: create_business_base

创建业务 Base，名称固定为：

```text
高管追踪与任务追踪数据中枢
```

创建成功后记录：

```text
AGENT_BASE_TOKEN={generated business base token}
```

不得向管理员索要 `AGENT_BASE_TOKEN`。创建失败时停止并报告接口错误。

## AGENT_ACTION: create_business_tables

在 `{AGENT_BASE_TOKEN}` 中创建四张表：

```text
高管追踪报告
任务信息表
任务跟进记录表
任务巡检报告
```

记录自动生成的 table_id：

```text
TABLE_ID_高管追踪报告
TABLE_ID_任务信息表
TABLE_ID_任务跟进记录表
TABLE_ID_任务巡检报告
```

不得向管理员索要这些 table_id。

## AGENT_ACTION: create_business_fields

字段必须严格按 v5 清单创建和校验。

### 高管追踪报告

```text
追踪人：用户字段
追踪报告：文本 / URL 文本
```

### 任务信息表

```text
任务编号：公式，主键，自动生成
任务标题：文本
详细描述：文本
负责人：单选用户
任务状态：单选
是否卡点：单选
截止日期：日期
创建人：系统字段，自动
任务跟进：双向链接，自动回填
跟进记录数：查找，自动
```

`任务状态` 选项必须为：

```text
待执行
进行中
已完成
已逾期
阻塞
```

`是否卡点` 选项必须为：

```text
是
否
```

### 任务跟进记录表

```text
跟进记录编号：公式，主键，自动
关联任务：单向链接，关联任务信息表
跟进内容：文本
创建人：系统字段，自动
创建时间：系统字段，自动
任务负责人：查找，自动
任务信息表：双向链接，自动回填
```

### 任务巡检报告

```text
巡检日期：日期
巡检报告：文本 / URL 文本
```

字段创建规则：

```text
可创建字段必须严格使用 v5 字段名和类型。
系统字段、公式字段、查找字段、双向链接字段如果不能通过 API 创建，必须报告具体限制，不得改成普通文本字段。
option_id 不强求沿用 v5 旧 ID，但选项名称必须一致。
字段创建失败时停止安装，报告表名、字段名、字段类型和接口错误。
不得新增 追踪周期、报告摘要、巡检摘要、风险数量。
```

## AGENT_ACTION: transfer_business_base_owner

如果能解析 `USER_OPEN_ID`，可执行所有者转让：

```bash
lark-cli --profile {APP_ID} --as bot drive permission.members transfer_owner \
  --token "{AGENT_BASE_TOKEN}" --type bitable \
  --data '{"member_type":"openid","member_id":"{USER_OPEN_ID}","perm":"full_access"}' \
  --old-owner-perm full_access --yes
```

无法解析 `USER_OPEN_ID` 时不要阻塞建表流程，记录原因后继续。

## AGENT_ACTION: resolve_business_table_ids

列出业务 Base 表：

```bash
lark-cli --profile {APP_ID} base +table-list --base-token {AGENT_BASE_TOKEN} --as bot --format json
```

按表名解析并确认不为空：

```text
TABLE_ID_高管追踪报告
TABLE_ID_任务信息表
TABLE_ID_任务跟进记录表
TABLE_ID_任务巡检报告
```

不要向管理员询问这些值。

验证表字段：

```bash
lark-cli --profile {APP_ID} base +field-list --base-token {AGENT_BASE_TOKEN} --table-id {TABLE_ID_高管追踪报告} --as bot >/dev/null
lark-cli --profile {APP_ID} base +field-list --base-token {AGENT_BASE_TOKEN} --table-id {TABLE_ID_任务信息表} --as bot >/dev/null
lark-cli --profile {APP_ID} base +field-list --base-token {AGENT_BASE_TOKEN} --table-id {TABLE_ID_任务跟进记录表} --as bot >/dev/null
lark-cli --profile {APP_ID} base +field-list --base-token {AGENT_BASE_TOKEN} --table-id {TABLE_ID_任务巡检报告} --as bot >/dev/null
```

字段验证要求：

```text
高管追踪报告：追踪人、追踪报告
任务信息表：任务编号、任务标题、详细描述、负责人、任务状态、是否卡点、截止日期、创建人、任务跟进、跟进记录数
任务跟进记录表：跟进记录编号、关联任务、跟进内容、创建人、创建时间、任务负责人、任务信息表
任务巡检报告：巡检日期、巡检报告
任务状态选项：待执行、进行中、已完成、已逾期、阻塞
是否卡点选项：是、否
```

## AGENT_ACTION: write_runtime_config

写入运行环境或任务配置：

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
LARK_APP_ID={APP_ID}
LARK_APP_SECRET={APP_SECRET}
FEISHU_APP_ID={APP_ID}
FEISHU_APP_SECRET={APP_SECRET}
FEISHU_BASE_TOKEN={AGENT_BASE_TOKEN}
FEISHU_TOKEN_BASE_TOKEN={TOKEN_BASE_TOKEN}
FEISHU_TOKEN_TABLE_ID={TOKEN_TABLE_ID}
FEISHU_EXEC_REPORT_TABLE_ID={TABLE_ID_高管追踪报告}
FEISHU_TASK_TABLE_ID={TABLE_ID_任务信息表}
FEISHU_TASK_TRACKING_TABLE_ID={TABLE_ID_任务跟进记录表}
FEISHU_TASK_REPORT_TABLE_ID={TABLE_ID_任务巡检报告}
```

## AGENT_ACTION: verify_collectors

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

## AGENT_ACTION: configure_task_cron

创建新的 task-tracking 巡检定时任务：

```yaml
schedule:
  cron: "0 21 * * *"
  tz: "Asia/Shanghai"
payload:
  kind: agentTurn
  message: |
    运行 task-tracking 每日巡检。
    读取任务信息表未完成任务，采集负责人近 7 天数据，
    判断进展/风险/逾期/完成状态，更新任务表并生成巡检报告。
```

创建后记录：

```text
TASK_TRACKING_CRON_JOB_ID={generated_job_id}
TASK_TRACKING_CRON="0 21 * * *"
TASK_TRACKING_CRON_TZ=Asia/Shanghai
```

## AGENT_ACTION: conversation_tests

```text
executive-tracking：对一个已授权成员生成高管追踪并写入高管追踪报告表。
task-tracking：通过对话创建一个小任务，写入任务信息表和任务跟进记录表。
task-tracking cron：dry-run 或手动触发一次每日巡检。
```

## AGENT_ACTION: final_verify

最终确认：

- 只暴露 `executive-tracking` 和 `task-tracking`。
- `feishu-user-token-registry` 不在本包内。
- 前置 Token 表已验证。
- 业务 Base 已自动创建。
- `AGENT_BASE_TOKEN` 由创建结果自动解析。
- 四张业务表 table_id 已按表名自动解析。
- 四张业务表字段已按 v5 字段清单创建并验证。
- shared/internal collector 存在。
- 高管追踪可写入 `高管追踪报告`。
- 任务追踪可写入 `任务信息表`、`任务跟进记录表`、`任务巡检报告`。
- task-tracking 定时任务已创建并记录 job id。
