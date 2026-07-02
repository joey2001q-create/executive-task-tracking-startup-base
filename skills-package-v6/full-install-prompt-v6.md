# 高管追踪 + 任务追踪安装提示词 v6

你收到一个压缩包 `skills-package-v6.zip`。这是正式瘦身版安装包，只保留两个业务入口：

- `executive-tracking`：高管追踪
- `task-tracking`：任务追踪

其他业务 skill（招聘、团队氛围、考勤、竞对分析、老板每日简报、客户跟进等）已移除，不得安装、不得配置、不得在选择卡片中展示。

## 铁律

1. 每一步执行完后必须验证，验证通过才进入下一步。
2. 验证失败立即停止，报告错误原因和已完成步骤，等待用户指示。
3. 只安装本包保留的两个业务入口：`executive-tracking` 和 `task-tracking`。
4. `feishu-data-collector-v3` 和 6 个 `feishu-*-collector` 是共享基础依赖，自动安装，不作为业务入口展示。
5. 高管横向对比 `feishu-executive-comparison` 作为高管追踪能力的一部分保留，不作为独立业务入口展示。
6. 用户授权与 Token 管理由外部流程维护；本安装流程只读取 token 表配置并验证采集组件存在。
7. 字段定义、权限清单、代码架构见同包 `agent-exec-config-v6.md`。

## 步骤 0：确认安装范围

本包没有可选业务范围，固定安装：

```text
INSTALL_SKILLS=("executive-tracking" "task-tracking")
```

向用户说明：

> 本次安装包只保留两个业务入口：高管追踪和任务追踪。底层飞书数据采集组件会自动安装；其他 skill 已清理，不会安装。

## 步骤 1：解压

```bash
mkdir -p /home/gem/workspace/agent/skills
unzip skills-package-v6.zip -d /home/gem/workspace/agent/skills/
```

如果 zip 解压后外层存在 `skills-package-v6/`，将其下内容移动到 `/home/gem/workspace/agent/skills/`，确保路径形如：

```text
/home/gem/workspace/agent/skills/feishu-boss-work/SKILL.md
/home/gem/workspace/agent/skills/feishu-exec-task-extractor/SKILL.md
```

### 验证 1

```bash
test -f /home/gem/workspace/agent/skills/feishu-boss-work/SKILL.md && echo "ok: executive-tracking"
test -f /home/gem/workspace/agent/skills/feishu-exec-task-extractor/SKILL.md && echo "ok: task-tracking"
test -f /home/gem/workspace/agent/skills/feishu-data-collector-v3/SKILL.md && echo "ok: data collector"
test -f /home/gem/workspace/agent/skills/agent-exec-config-v6.md && echo "ok: exec config"
test ! -d /home/gem/workspace/agent/skills/hire-recruit
test ! -d /home/gem/workspace/agent/skills/team-vibe-tracker
test ! -d /home/gem/workspace/agent/skills/attendance-report
test ! -d /home/gem/workspace/agent/skills/competitor-intelligence-v2
test ! -d /home/gem/workspace/agent/skills/feishu-customer-follow-tracker
```

通过条件：两个业务入口存在，共享采集层存在，已移除业务不存在。

## 步骤 2：安装 Python 依赖

```bash
python3 -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple requests
```

### 验证 2

```bash
python3 - <<'PY'
import requests
print("ok: feishu tracking deps")
PY
```

## 步骤 3：读取执行配置

读取：

```text
/home/gem/workspace/agent/skills/agent-exec-config-v6.md
```

只执行其中与以下标签相关的内容：

```text
verify_package_scope
install_dependencies
verify_credentials
verify_permissions
write_runtime_config
verify_collectors
configure_task_cron
final_verify
```

### 验证 3

```bash
grep -c "AGENT_ACTION:" /home/gem/workspace/agent/skills/agent-exec-config-v6.md
```

通过条件：数量不少于 8。

## 步骤 4：获取应用凭证

从入站上下文元数据获取 `account_id`，通过 `gateway config.get` 解析 App ID 和 App Secret。无法自动获取则询问用户：

```text
请提供飞书自建应用的 App ID 和 App Secret。
```

### 验证 4

```bash
lark-cli --profile {APP_ID} api POST /open-apis/auth/v3/tenant_access_token/internal \
  --data '{"app_id":"{APP_ID}","app_secret":"{APP_SECRET}"}' 2>&1 | grep -q "tenant_access_token"
```

## 步骤 5：权限检查与授权

只申请高管追踪和任务追踪需要的权限。不要申请招聘、考勤、竞对、老板每日简报、客户跟进权限。

从 `agent-exec-config-v6.md` 读取 scope 清单，生成 URL 编码后的飞书开放平台授权链接。每条链接 scope 数量控制在 22 个以内。

告知用户：

> 请按顺序点击权限链接，开通高管追踪、任务追踪和共享数据采集所需权限。开通后请发布版本或开启调试模式，并将通讯录权限范围设为「全部成员」。

### 验证 5

```bash
lark-cli --profile {APP_ID} api GET "/open-apis/im/v1/chats?page_size=1" --as bot 2>&1 | grep -q "code.*0" && echo "ok: im" || echo "fail: im"
lark-cli --profile {APP_ID} api GET "/open-apis/contact/v3/departments?page_size=1" --as bot 2>&1 | grep -q "code.*0" && echo "ok: contact" || echo "fail: contact"
```

## 步骤 6：配置 Base 与 Token 表

询问或解析以下变量：

```text
AGENT_BASE_TOKEN
TABLE_ID_高管追踪报告
TABLE_ID_任务信息表
TABLE_ID_任务跟进记录表
TABLE_ID_任务巡检报告
TOKEN_BASE_TOKEN
TOKEN_TABLE_ID
BOSS_OPEN_ID
```

只校验这几张表。不要校验招聘、考勤、竞对、客户跟进等旧表。

### 验证 6

```bash
lark-cli --profile {APP_ID} base +field-list --base-token {AGENT_BASE_TOKEN} --table-id {TABLE_ID_高管追踪报告} --as bot >/dev/null
lark-cli --profile {APP_ID} base +field-list --base-token {AGENT_BASE_TOKEN} --table-id {TABLE_ID_任务信息表} --as bot >/dev/null
lark-cli --profile {APP_ID} base +field-list --base-token {AGENT_BASE_TOKEN} --table-id {TABLE_ID_任务跟进记录表} --as bot >/dev/null
lark-cli --profile {APP_ID} base +field-list --base-token {AGENT_BASE_TOKEN} --table-id {TABLE_ID_任务巡检报告} --as bot >/dev/null
```

## 步骤 7：写入运行配置

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

## 步骤 8：验证共享采集层

```bash
test -f /home/gem/workspace/agent/skills/feishu-data-collector-v3/bin/feishu-data-collector-v3
test -f /home/gem/workspace/agent/skills/feishu-calendar-collector/bin/feishu-calendar-collector
test -f /home/gem/workspace/agent/skills/feishu-task-collector/bin/feishu-task-collector
test -f /home/gem/workspace/agent/skills/feishu-minutes-collector/bin/feishu-minutes-collector
test -f /home/gem/workspace/agent/skills/feishu-group-collector/bin/feishu-group-collector
test -f /home/gem/workspace/agent/skills/feishu-p2p-collector/bin/feishu-p2p-collector
test -f /home/gem/workspace/agent/skills/feishu-mail-collector/bin/feishu-mail-collector
```

## 步骤 9：配置任务追踪定时巡检

任务追踪需要每日巡检未完成任务，默认每天 21:00：

```yaml
schedule:
  cron: "0 21 * * *"
  tz: "Asia/Shanghai"
payload:
  kind: agentTurn
  message: |
    运行 task-tracking 每日巡检。
    读取任务信息表未完成任务，采集负责人近 7 天数据，判断进展/风险/逾期/完成状态，更新任务表并生成巡检报告。
```

## 步骤 10：最终验证

```bash
find /home/gem/workspace/agent/skills -maxdepth 2 -name SKILL.md | sort
```

必须看到：

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

不得看到：

```text
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

最终报告：

```text
已完成高管追踪 executive-tracking 和任务追踪 task-tracking 的安装。
共享采集底座已安装。
其他业务 skill 未安装。
```
