---
name: feishu-executive-tracker-v2
description: |
  飞书高管工作追踪 Skill v2。只负责【分析+输出】，数据采集由 feishu-data-collector-v3 统一提供。
  输出维度：关键事项、关键决策、重大风险、需老板介入、管理风格。
  生成 L1 聊天简报 + L2 云文档详情（bot 身份创建）+ 自动写入追踪台账。
---

# 飞书高管工作追踪 v2

## 架构（分层解耦）

```
本 Skill（feishu-boss-work）
  ├─ 输入：标准化数据（由 feishu-data-collector-v3 提供）
  ├─ 处理：AI 分析 → 4 维度简报
  └─ 输出：L1 聊天简报 + L2 云文档 + 台账写入

feishu-data-collector-v3（数据获取层）
  ├─ 单聊采集 skill（feishu-p2p-collector）
  ├─ 群聊采集 skill（feishu-group-collector）
  ├─ 日程采集 skill（feishu-calendar-collector）
  ├─ 任务采集 skill（feishu-task-collector）
  ├─ 妙记采集 skill（feishu-minutes-collector）
  ├─ 邮箱采集 skill（feishu-mail-collector）
  └─ 其他扩展 skill
```

**铁律：本 skill 不直接调 lark-cli 采数据，只调 feishu-data-collector-v3。**

## 使用边界

仅在已授权的企业管理场景中使用。数据范围限于公司账号和工作空间。

- 优先使用摘要、证据 ID、时间戳、参与人和业务主题，不默认输出完整原文。
- 排除个人、医疗、家庭、个人财务、员工组织活动、法律特权信息或与工作无关的私人内容。
- 不协助绕过飞书权限、恢复已删除内容、抓取私人设备数据或进行隐蔽监控。

## 快速流程

1. **调用数据获取**：对每位高管，调用 `feishu-data-collector-v3` 获取指定时间范围的 6 类数据（日程、任务、妙记、群聊、单聊、邮箱）。
2. **数据校验**：确认数据完整性，记录缺口。
3. **AI 分析**：按 4 维度分析框架处理数据。
4. **生成输出**：
   - L1 聊天框简报（飞书原生格式）
   - L2 云文档详情（markdown → 飞书文档，bot 身份创建）
5. **写入台账**：自动写入追踪多维表。

## 范围定义

- `report_date` / 周期：自然工作日范围，含时区。
- `executives`：高管姓名 + 飞书 open_id。
- `sources`：默认全部（日程/任务/单聊/群聊/妙记/邮箱），可指定子集。
- `business_priorities`：公司当前 OKR、重点项目、风险主题。

## 4 维度分析框架

只输出这 4 个维度，没有就写「无」：

### 1. 🎯 关键事项
- 本周核心工作投入，1-3 条
- 与公司战略/重点项目/客户相关的实质性推进
- 避免：日常状态同步、无结果的讨论

### 2. ✅ 关键决策
- 高管做出的重要决定：方案选择、预算批准、优先级调整、人员授权等
- 含：决策内容、理由、影响范围、下一步
- 没有就写「无」，不硬凑

### 3. ⚠️ 重大风险
- 客户流失、项目延期、质量问题、合规风险、内部冲突、交付边界不清等
- 含：风险内容、严重程度、当前处理状态、是否需要 CEO 支持
- 没有就写「无」

### 4. 🙋 需老板介入
- 超出高管权限的决策、战略取舍、未解决冲突、需要 CEO 拍板的事项
- 明确写「建议动作」
- 没有就写「无」，让老板放心

**分析原则：**
- 区分「活动」和「影响」，不要把消息多、会议长直接当产出。
- 对推断使用「可见数据表明…」措辞。
- 没找到证据时写「已采集来源中未发现相关证据」，不要写「没有做」。

## 数据获取

**调用 feishu-data-collector-v3：**

```bash
python3 feishu-data-collector-v3 /tmp/<name>_data.json '<open_id>:<姓名>'
```

- 自动从多维表读取 token
- 自动采集 6 类数据（日程/任务/妙记/群聊/单聊/邮箱）
- 自动处理分页
- 输出标准化 JSON（见 `references/data-contract.md`）

**如 feishu-data-collector-v3 不可用**，临时 fallback 使用底层采集 skill：
- 日程：`feishu-calendar-collector collect --user <oid> --start <> --end <>`
- 任务：`feishu-task-collector collect --user <oid>`
- 单聊：`feishu-p2p-collector collect --user <oid> --start <> --end <>`
- 群聊：`feishu-group-collector collect --user <oid> --start <> --end <>`
- 妙记：`feishu-minutes-collector collect --user <oid> --start <> --end <>`
- 邮箱：`feishu-mail-collector collect --user <oid> --max 50`

## 输出标准

### L1 聊天框简报（飞书原生格式）

飞书 IM 不渲染 markdown（`###`、`| 表格 |`、`**` 都显示原始文本），必须使用**纯文本 + emoji + 对齐空格**。

```
**📊 [姓名] · [职位] · 工作追踪（YYYY-MM-DD ~ YYYY-MM-DD）**
**🎯 关键事项**
- [核心工作1]
- [核心工作2]

**✅ 关键决策**
- [决策内容；无则写「无」]

**⚠️ 重大风险**
- [风险内容；无则写「无」]

**🙋 需要老板介入**
- [需拍板事项；无则写「无」]

**🤔 本次管理风格**
- [高管管理风格：战略推进/跨部门协调/团队管理/客户处理/风险收敛/执行跟进等]

**📄 工作详情**  [https://...](https://...)
```

**写作要求：**
- 标题和维度名加粗 `**`
- 内容用 `-` 列表
- 每条一句话，动词开头，带结果/状态
- 宁缺毋滥，没有就写「无」
- 客户名/项目名保留，个人隐私脱敏
- 去掉数据汇总行，直接放底部云文档链接

### L2 云文档详情

用 `lark-cli docs +create --api-version v2` 创建飞书文档（**bot 身份**，去掉 `--as user`，更稳定且老板可见）。

详情文档包含：
- 每位高管的 4 维度分析详情
- 具体工作主题、任务、日程、聊天线索
- 每个强结论的证据 ID、来源类型、时间、置信度
- 源数据覆盖状态和数据缺口

聊天框最终只返回：简报 + "详情已写入云文档：<链接>"

## 写入追踪台账多维表（必做）

base_token：`{{AGENT_BASE_TOKEN}}`
table_id：`{{TABLE_ID_高管追踪报告}}`

```bash
lark-cli base +record-upsert \
  --base-token "{{AGENT_BASE_TOKEN}}" \
  --table-id "{{TABLE_ID_高管追踪报告}}" \
  --json '{"追踪人":[{"id":"<高管open_id>"}],"追踪报告":"<云文档链接>"}' \
  --as bot \
  --profile {{APP_ID}}
```
（bot 身份写入，无需 `--as user`）

防重复：先 `base +record-list` 查现有记录，同一高管+同一周期已有则更新。


## 质量检查

- 确认日期和时区过滤正确
- 确认每位高管、每类来源至少有一种状态：已采集/不可用/权限拒绝/无记录
- 确认高敏感信息已摘要、脱敏或省略
- 确认老板简报没有暴露工作流水账
- 确认详情云文档已创建，聊天框只返回链接
- 确认台账已写入
