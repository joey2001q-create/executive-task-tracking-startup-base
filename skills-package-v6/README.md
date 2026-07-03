# Skills Package v6

这是高管追踪和任务追踪的正式瘦身业务包。

## 包含的业务入口

- `executive-tracking`：高管追踪，对应 `feishu-boss-work/`
- `task-tracking`：任务追踪，对应 `feishu-exec-task-extractor/`

## 前置条件

安装本包前，必须先完成单独的前置授权包：

```text
feishu-user-token-registry-package-v6.zip
```

前置包负责：

- 复制 Token 表模板。
- 开启 Token 表所有 workflows。
- 发送成员授权卡片。
- 让成员授权并写入 token。
- 验证 `TOKEN_BASE_TOKEN` 和 `TOKEN_TABLE_ID`。

## v6 业务包负责什么

`skills-package-v6.zip` 不再要求管理员手动提供业务 Base 和四个业务表 ID。

正确逻辑是：

```text
Agent 安装 skills-package-v6
-> Agent 自动创建业务 Base「高管追踪与任务追踪数据中枢」
-> Agent 按 v5 字段清单创建四张业务表
-> Agent 自动解析 AGENT_BASE_TOKEN
-> Agent 按表名解析四张业务表 table_id
-> Agent 写入运行配置
-> Agent 创建 task-tracking 定时任务
-> 管理员开始对话测试
```

业务 Base：

```text
名称：高管追踪与任务追踪数据中枢
创建方式：Agent 自动创建
```

必须按 v5 字段清单创建并自动解析的业务表：

```text
高管追踪报告
任务信息表
任务跟进记录表
任务巡检报告
```

字段来源是 v5 原定义，不是 v6 主观设计：

```text
高管追踪报告：feishu-boss-work/SKILL.md
任务信息表：feishu-exec-task-extractor/references/field-mapping.md
任务跟进记录表：feishu-exec-task-extractor/references/field-mapping.md
任务巡检报告：feishu-exec-task-extractor/SKILL.md
```

## 给 Agent 的安装入口

把 `skills-package-v6.zip` 发给 Agent 后，让它先读：

```text
full-install-prompt-v6.md
```

推荐提示词：

```text
请解压并安装 skills-package-v6.zip。
解压后不要自行推断流程，必须先读取包内 full-install-prompt-v6.md。
按文档执行：先验证前置 Token 表，然后自动创建业务 Base「高管追踪与任务追踪数据中枢」，按 v5 字段清单创建四张业务表，自动解析 AGENT_BASE_TOKEN 和四张业务表 table_id。
APP_SECRET 必须由你从已绑定应用、运行时安全配置、lark-cli profile 或前置配置中读取，不要在聊天里向我索要或要求我粘贴。
不要向我索要 AGENT_BASE_TOKEN 或四个业务表 TABLE_ID，这些必须由你自动创建业务 Base 和业务表后按表名自动解析。
```

## shared/internal 依赖

这些目录是两个业务入口的内部依赖，不作为用户可选业务 skill 展示：

- `feishu-data-collector-v3/`
- `feishu-calendar-collector/`
- `feishu-task-collector/`
- `feishu-minutes-collector/`
- `feishu-group-collector/`
- `feishu-p2p-collector/`
- `feishu-mail-collector/`
- `feishu-executive-comparison/`

## 重要边界

- 本包不包含 `feishu-user-token-registry`。
- 本包不发送授权卡片。
- 本包只读取已验证的 Token 表。
- 本包会自动创建业务 Base 和四张业务表。
- 本包字段必须来自 v5 原定义，不得主观新增、删减、改名或改类型。
- 本包不应向管理员索要 `AGENT_BASE_TOKEN` 或业务表 `TABLE_ID`。
- 不要把真实 App Secret、Token、Base Token、Table ID、授权码、user token、refresh token、cron job id 写入 GitHub、skill 源码、zip 包源码、日志或公开文档。
