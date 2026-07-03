# 高管追踪 + 任务追踪安装提示词 v6

你收到的是 `skills-package-v6.zip`。这是正式瘦身业务包，只面向两个业务入口：

- `executive-tracking`：高管追踪
- `task-tracking`：任务追踪

本包不包含 `feishu-user-token-registry`。成员授权和 Token 表必须已由前置 registry 包完成并验证。

## 正确端到端流程

```text
Agent 安装 registry
-> Agent 复制 Token 表模板并开启所有 workflows
-> 管理员手动配置飞书应用权限、回调地址、应用可用范围和发布
-> 管理员说“给 XX 发授权卡片”
-> Agent 发送授权卡片
-> 成员授权，token 写入 Token 表
-> Agent 验证 Token 表
-> Agent 安装 skills-package-v6
-> Agent 校验并复制业务模板 Base，生成业务数据中枢
-> Agent 从复制结果解析并记录 AGENT_BASE_TOKEN
-> Agent 按表名解析并记录高管追踪和任务追踪所需 table_id
-> Agent 创建 task-tracking 定时任务
-> 管理员通过对话测试高管追踪和任务追踪
```

本文件从 `Agent 安装 skills-package-v6` 开始执行。不要跳过业务模板 Base 校验、复制和表结构校验步骤。

## 核心规则

1. 每一步执行完必须验证，验证通过才进入下一步。
2. 验证失败立即停止，报告失败步骤、错误信息和已完成步骤。
3. 只暴露 `executive-tracking` 和 `task-tracking` 两个业务入口。
4. shared/internal collector 自动安装，但不要作为用户可选 skill 展示。
5. Token 表只读取已验证的前置 registry 结果，不在本包内创建或发送授权卡片。
6. 业务 Base 必须由 Agent 从指定业务模板 Base 复制生成，不要自行新建空 Base，也不要向管理员索要 `AGENT_BASE_TOKEN` 或四个业务 `TABLE_ID`。
7. 不要把 App Secret、Token、Base Token、Table ID、授权码、user token、refresh token、cron job id 写入 GitHub、skill 源码或公开文档。
8. `BOSS_OPEN_ID` 优先从当前对话用户/管理员身份解析；无法解析时，只询问一次。
9. 创建 task-tracking 定时任务后，记录真实生成的 job id，不要写死。
10. 业务表字段结构以指定模板 Base 为准。复制模板后只做校验，不要主观新增、删减、改名或改类型。
11. 不要查找、索要或依赖任何历史版本包；安装时只读取当前 `skills-package-v6.zip` 内的文档和文件。
12. 不得新增主观字段：`追踪周期`、`报告摘要`、`巡检摘要`、`风险数量`。

## Step 0：确认前置 Registry 已完成

先确认前置授权包已经完成：

```text
feishu-user-token-registry 已安装。
Token 多维表格已复制生成。
Token 表 workflows 已全部 Enable。
飞书应用权限、回调地址、应用可用范围和发布已由管理员完成。
目标成员至少一人已完成授权。
Token 表中存在有效 user_access_token 和 refresh_token。
TOKEN_BASE_TOKEN 和 TOKEN_TABLE_ID 可由 Agent 从前置流程运行时记录、Token 表配置行或管理员明确输入读取。
```

如果没有完成，停止安装，让用户先完成 registry 流程。

## Step 1：解压业务包

```bash
mkdir -p /home/gem/workspace/agent/skills
unzip skills-package-v6.zip -d /home/gem/workspace/agent/skills/
```

如果 zip 解压后存在外层 `skills-package-v6/` 目录，将其下 skill 目录和文档移动到：

```text
/home/gem/workspace/agent/skills/
```

验证：

```bash
test -f /home/gem/workspace/agent/skills/feishu-boss-work/SKILL.md
test -f /home/gem/workspace/agent/skills/feishu-exec-task-extractor/SKILL.md
test -f /home/gem/workspace/agent/skills/feishu-data-collector-v3/SKILL.md
test -f /home/gem/workspace/agent/skills/agent-exec-config-v6.md
test ! -d /home/gem/workspace/agent/skills/feishu-user-token-registry
```

## Step 2：安装依赖

```bash
python3 -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple requests
```

验证：

```bash
python3 - <<'PY'
import requests
print("ok: requests")
PY
```

## Step 3：读取执行配置

读取：

```text
/home/gem/workspace/agent/skills/agent-exec-config-v6.md
```

只执行其中与以下标签相关的内容：

```text
verify_package_scope
install_dependencies
verify_credentials
verify_registry_token_table
setup_business_base
resolve_business_table_ids
write_runtime_config
verify_collectors
configure_task_cron
conversation_tests
final_verify
```

## Step 4：解析应用凭证和 Token 表配置

从已绑定的飞书应用 profile、应用运行时安全配置、前置 registry 运行时记录或 Token 表配置行读取：

```text
APP_ID
APP_SECRET
TOKEN_BASE_TOKEN
TOKEN_TABLE_ID
```

注意：

- `APP_SECRET` 是应用侧安全凭证，必须由 Agent 从已绑定应用、运行时安全配置、lark-cli profile 或前置配置中读取。
- 不要在聊天里向管理员索要或要求粘贴 `APP_SECRET`。
- 如果无法读取 `APP_SECRET`，停止安装并提示管理员先完成飞书应用绑定/运行时凭证配置；不要让管理员把 secret 发在对话里。
- 这里不能要求管理员提供 `AGENT_BASE_TOKEN` 或业务表 `TABLE_ID`。
- `AGENT_BASE_TOKEN` 必须由后续模板 Base 复制结果生成。
- 业务表 `TABLE_ID` 必须由复制后的业务 Base 按表名自动解析。

验证应用凭证：

```bash
lark-cli --profile {APP_ID} api POST /open-apis/auth/v3/tenant_access_token/internal \
  --data '{"app_id":"{APP_ID}","app_secret":"{APP_SECRET}"}' 2>&1 | grep -q "tenant_access_token"
```

## Step 5：验证前置 Token 表

只验证已有 Token 表，不创建 registry：

```bash
lark-cli --profile {APP_ID} base +field-list --base-token {TOKEN_BASE_TOKEN} --table-id {TOKEN_TABLE_ID} --as bot >/dev/null
```

Token 表必须包含：

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

至少一名目标成员应满足：

```text
user_access_token 存在
refresh_token 存在
授权状态=有效
```

## Step 6：复制业务模板 Base

业务数据中枢必须由 Agent 从指定业务模板 Base 复制生成，不要自行新建空 Base，不要手动重建字段。

业务模板 Base：

```text
模板链接：https://ldkj.feishu.cn/base/XDvOblimtagfxzsyD5ncxuWHn5I?from=from_copylink
TEMPLATE_BASE_TOKEN=XDvOblimtagfxzsyD5ncxuWHn5I
复制后的业务 Base 名称：高管追踪与任务追踪数据中枢
```

复制前先验证模板可读：

```bash
lark-cli --profile {APP_ID} base +base-get --base-token XDvOblimtagfxzsyD5ncxuWHn5I --as bot
lark-cli --profile {APP_ID} base +table-list --base-token XDvOblimtagfxzsyD5ncxuWHn5I --as bot --format json
```

必须能看到以下四张表：

```text
高管追踪报告
任务信息表
任务跟进记录表
任务巡检报告
```

复制模板结构，不复制数据：

```bash
lark-cli --profile {APP_ID} base +base-copy \
  --base-token XDvOblimtagfxzsyD5ncxuWHn5I \
  --name "高管追踪与任务追踪数据中枢" \
  --without-content \
  --as bot
```

从返回结果优先提取 `app_token`，兼容兜底 `base_token`，记录为：

```text
AGENT_BASE_TOKEN={COPIED_BUSINESS_BASE_TOKEN}
```

不得向管理员索要 `AGENT_BASE_TOKEN`。如果模板不可读、复制失败、或复制结果中无法解析 `app_token/base_token`，立即停止并报告具体错误。

如果能解析 `USER_OPEN_ID`，将复制后的 Base 所有者转让给管理员，Bot 保留 full_access；无法解析时不要编造用户 ID，报告限制并继续后续表结构校验。

## Step 7：解析业务表 ID 并校验结构

不要手动创建业务表，不要手动重建字段。必须从复制后的 `{AGENT_BASE_TOKEN}` 中按表名解析并记录：

```text
TABLE_ID_高管追踪报告={generated table_id}
TABLE_ID_任务信息表={generated table_id}
TABLE_ID_任务跟进记录表={generated table_id}
TABLE_ID_任务巡检报告={generated table_id}
```

不得向管理员索要这四个 table_id。

### 字段校验规则

- 字段结构以业务模板 Base 为准。
- 复制模板时必须使用 `--without-content`，只复制结构，不复制数据。
- 不要手动新增、删除、改名或改类型。
- 不要用自造字段替代模板字段。
- 如果复制后的模板缺少业务必需字段、字段类型不一致、公式/查找/关联关系异常，立即停止并报告具体表名、字段名和差异。
- 如果飞书 API 无法完整读取某类字段元信息，必须报告“无法验证的字段类型和原因”，不要假装验证通过。

## Step 8：验证业务表和字段

列出业务 Base 中的表：

```bash
lark-cli --profile {APP_ID} base +table-list --base-token {AGENT_BASE_TOKEN} --as bot --format json
```

必须只围绕以下四张表继续安装：

```text
高管追踪报告
任务信息表
任务跟进记录表
任务巡检报告
```

逐表验证字段：

```bash
lark-cli --profile {APP_ID} base +field-list --base-token {AGENT_BASE_TOKEN} --table-id {TABLE_ID_高管追踪报告} --as bot >/dev/null
lark-cli --profile {APP_ID} base +field-list --base-token {AGENT_BASE_TOKEN} --table-id {TABLE_ID_任务信息表} --as bot >/dev/null
lark-cli --profile {APP_ID} base +field-list --base-token {AGENT_BASE_TOKEN} --table-id {TABLE_ID_任务跟进记录表} --as bot >/dev/null
lark-cli --profile {APP_ID} base +field-list --base-token {AGENT_BASE_TOKEN} --table-id {TABLE_ID_任务巡检报告} --as bot >/dev/null
```

验证通过条件：

```text
四张表均存在。
四张表字段可读取。
字段结构保持模板复制结果，没有被 Agent 手动新增、删除、改名或改类型。
如发现字段缺失、类型异常、公式/查找/关联关系异常，已停止并报告差异。
```

如果缺表或字段异常，停止安装，报告缺失项或异常项。不要向管理员索要 table_id，也不要手工创建字段替代。

## Step 9：解析 BOSS_OPEN_ID

`BOSS_OPEN_ID` 优先取当前安装/测试对话中的管理员 open_id，或从前置 Token 表中已授权的老板/管理员记录解析。

如果无法自动解析，只问一次：

```text
请提供老板/管理员的 open_id，用于任务布置人与巡检失败通知。
```

## Step 10：写入运行配置

写入运行环境、Agent runtime notes 或任务配置：

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

兼容 collector 的环境变量也要写入：

```text
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

## Step 11：验证共享采集层

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

## Step 12：创建 task-tracking 定时任务

安装 v6 时必须创建新的任务巡检定时任务。不要假设已有 job id。

默认每天北京时间 21:00，时区必须显式设置为 `Asia/Shanghai`：

```yaml
schedule:
  cron: "0 21 * * *"
  tz: "Asia/Shanghai"
payload:
  kind: agentTurn
  message: |
    运行 task-tracking 每日巡检。
    读取任务信息表未完成任务，采集负责人近 7 天飞书数据，
    判断进展/风险/逾期/完成状态，更新任务表、追加跟进记录，并生成巡检报告。
```

创建后记录：

```text
TASK_TRACKING_CRON_JOB_ID={generated_job_id}
TASK_TRACKING_CRON="0 21 * * *"
TASK_TRACKING_CRON_TZ=Asia/Shanghai
TASK_TRACKING_CRON_TIME_DESC=北京时间每天 21:00
```

## Step 13：对话测试

至少完成两个测试：

```text
高管追踪测试：对一个已授权成员运行 executive-tracking，并写入高管追踪报告表。
任务追踪测试：通过对话创建一个小任务，确认写入任务信息表和任务跟进记录表。
任务巡检测试：dry-run 或手动触发一次 task-tracking 巡检。
```

## Step 14：最终报告

最终输出：

```text
executive-tracking 和 task-tracking 已安装。
前置 Token 表已验证。
业务 Base 已从指定模板复制生成。
AGENT_BASE_TOKEN 已从复制结果自动解析。
四张业务表 table_id 已按表名自动解析并验证。
四张业务表字段结构已按模板复制结果校验通过。
shared/internal collector 已安装。
task-tracking 定时任务已创建并记录 job id。
可以开始通过对话测试高管追踪和任务追踪。
```
