---
name: feishu-data-collector-v3
description: |
  飞书数据统一采集器 v3 — 基于多维表 token 直接调用飞书 API。
  支持6类数据：日程、任务、妙记、群聊、单聊、邮箱。
  作为高管追踪、日报等上层 skill 的数据获取层。

  触发场景：
  - 高管追踪需要采集某人的工作数据
  - 日报需要汇总个人数据
  - 任何需要读取用户个人飞书数据的场景
alwaysActive: false
---

# 飞书数据统一采集器 v3

## 作用

为上层 skill（高管追踪、日报等）提供**标准化、可靠、可复用**的数据获取能力。

**核心设计：**
- 从多维表读取用户 token
- 直接调用飞书 API，不依赖 lark-cli --as user
- 返回统一的标准化 JSON，上层直接消费

## 使用方式

### 命令行

```bash
python3 feishu-data-collector-v3 <output.json> <oid:name> [<oid:name> ...]
```

示例：
```bash
python3 feishu-data-collector-v3 /tmp/han_data.json 'ou_xxx:韩嘉辉'
```

采集周期：默认过去 7 天

### 支持的数据源（6类）

| 数据源 | API 端点 | 说明 |
|--------|---------|------|
| 日程 | `/calendar/v4/calendars/primary/events/instance_view` | 需时间范围 |
| 任务 | `/task/v2/task_v2/list_related_task` | 无时间过滤 |
| 群聊 | `/im/v1/messages/search` | 需时间范围 |
| 单聊 | `/im/v1/messages/search` (chat_type=p2p) | 需时间范围 |
| 妙记 | `/minutes/v1/minutes/search` | 需时间范围 |
| 邮箱 | `/mail/v1/user_mailboxes/me/messages` | 需 label_id |

### 返回格式

```json
{
  "period": {"start": "...", "end": "..."},
  "executives": [
    {
      "user": "姓名",
      "open_id": "ou_xxx",
      "period": "...",
      "sources": {
        "calendar": {"ok": true, "code": 0, "data": {...}},
        "task": {"ok": true, "code": 0, "data": {...}},
        "minutes": {"ok": true, "code": 0, "data": {...}},
        "group": {"ok": true, "code": 0, "data": {...}},
        "p2p": {"ok": true, "code": 0, "data": {...}},
        "mail": {"ok": true, "code": 0, "data": {...}}
      }
    }
  ]
}
```

## Token 来源

从外部用户 token 表读取：`{{TOKEN_BASE_TOKEN}}` / `{{TOKEN_TABLE_ID}}`。该表不属于本安装包复制出的总 Base。

**前提**：用户 Token 已由外部流程写入 `{{TOKEN_BASE_TOKEN}}` / `{{TOKEN_TABLE_ID}}` 对应多维表。

## 数据源详解

### 1. 日程（calendar）

- API: `GET /calendar/v4/calendars/primary/events/instance_view`
- 参数: `start_time`, `end_time`（Unix 时间戳）
- 返回: `data.items[]`

### 2. 任务（task）

- API: `GET /task/v2/task_v2/list_related_task`
- 参数: `user_id_type=open_id`, `page_size`
- 返回: `data.items[]`

### 3. 妙记（minutes）

- API: `POST /minutes/v1/minutes/search`
- Body: `filter.create_time.start_time`, `filter.create_time.end_time`
- 返回: `data.items[]`

### 4. 群聊（group）

- API: `POST /im/v1/messages/search`
- Body: `query`, `start_time`, `end_time`
- 返回: `data.items[]`

### 5. 单聊（p2p）

- API: `POST /im/v1/messages/search`
- Body: `query`, `start_time`, `end_time`, `chat_type="p2p"`
- 返回: `data.items[]`

### 6. 邮箱（mail）⭐

- API: `GET /mail/v1/user_mailboxes/me/messages`
- 参数: `label_id=INBOX`, `page_size`
- **注意**：必须使用 `label_id` 参数，不能用 `folder_id`
- 返回: `data.messages[]`

## 子Skill拆分

v3 版本将6类数据采集拆分为独立的子Skill，便于单独调用和维护：

| 子Skill | 路径 | 用途 |
|---------|------|------|
| `feishu-calendar-collector` | `skills/feishu-calendar-collector/` | 日程采集 |
| `feishu-task-collector` | `skills/feishu-task-collector/` | 任务采集 |
| `feishu-minutes-collector` | `skills/feishu-minutes-collector/` | 妙记采集 |
| `feishu-group-collector` | `skills/feishu-group-collector/` | 群聊采集 |
| `feishu-p2p-collector` | `skills/feishu-p2p-collector/` | 单聊采集 |
| `feishu-mail-collector` | `skills/feishu-mail-collector/` | 邮件采集 |

每个子Skill都是独立的可执行脚本，直接从多维表读取token，返回标准化JSON。

### 子Skill用法

```bash
# 日程
feishu-calendar-collector collect --user ou_xxx --start "2026-06-14T00:00:00+08:00" --end "2026-06-21T23:59:59+08:00"

# 任务
feishu-task-collector collect --user ou_xxx

# 群聊
feishu-group-collector collect --user ou_xxx --start "..." --end "..."

# 单聊
feishu-p2p-collector collect --user ou_xxx --partners ou_yyy --start "..." --end "..."

# 妙记
feishu-minutes-collector collect --user ou_xxx --start "..." --end "..."

# 邮件
feishu-mail-collector collect --user ou_xxx --label-id INBOX
```

## Token 安全传递规则（铁律）

**严禁直接用 shell 变量传递长 token！**

### 错误做法（会导致token截断/损坏）
```bash
# ❌ 错误：shell变量传递长token
TOKEN="eyJhbGciOiJFUzI1Ni...6625字符..."
curl -H "Authorization: Bearer $TOKEN" ...
```

### 正确做法
```bash
# ✅ 方式1：用Python直接读取多维表并调用API（推荐）
python3 << 'PYEOF'
import requests
# 从多维表获取token → 直接调用API
PYEOF

# ✅ 方式2：写入临时文件传递
token_file=$(mktemp)
echo "$token" > "$token_file"
python3 -c "
import requests
with open('$token_file') as f:
    token = f.read().strip()
# 调用API...
"
rm -f "$token_file"

# ✅ 方式3：使用外部 token 管理能力
# 由外部 token 管理流程以目标用户身份运行 lark-cli 或直接调用 API
```

### 子Skill实现方式
所有子Skill已改为 **Python 脚本**，内部直接从多维表读取 token，避免了 shell 传递问题。

## 依赖

- `requests`（Python HTTP 库）
- 外部 token 管理流程（token 管理，存入多维表）
- 多维表: `{{TOKEN_BASE_TOKEN}}` / `{{TOKEN_TABLE_ID}}`

## 故障排查

**Q: 采集时报 token 过期？**
A: token 已过期，需要用户重新授权并提供新 code，执行 exchange 更新多维表。

**Q: 邮箱采集返回空？**
A: 可能原因：
- 用户没有邮件数据
- 飞书邮件企业版未开通
- 用户未授权邮件相关 scope

**Q: 某类数据返回 code 错误？**
A: 检查 token 是否包含对应 scope。如缺少 scope，需要重新授权。

**Q: 日程API返回99992402？**
A: 可能是时间参数格式问题。正确格式：`time_min` 和 `time_max` 为 Unix 时间戳（秒）。子Skill已自动处理ISO时间到Unix时间戳的转换。
