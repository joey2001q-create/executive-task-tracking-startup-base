# 数据契约

在总结前，将所有飞书来源数据标准化为以下结构。可以按需要增加字段，但核心字段应保持稳定。

## 报告输入

```json
{
  "report_date": "2026-06-09",
  "timezone": "Asia/Shanghai",
  "business_priorities": [
    {
      "id": "P1",
      "name": "Q2 企业销售签约",
      "owner": "CRO",
      "keywords": ["企业客户", "续约", "pipeline", "回款"]
    }
  ],
  "executives": [
    {
      "id": "exec_001",
      "name": "张伟",
      "title": "CRO",
      "feishu_open_id": "ou_xxx",
      "email": "zhang@example.com",
      "department": "销售部"
    }
  ],
  "source_status": [
    {
      "executive_id": "exec_001",
      "source_type": "chat",
      "status": "collected",
      "records": 184,
      "coverage_scope": "executive_to_all_authorized_employees",
      "notes": "已采集高管与企业内授权成员的单聊，以及高管参与或被提及的业务群；按策略排除无授权或私人内容。"
    }
  ],
  "output_targets": {
    "chat_brief": true,
    "detail_doc": {
      "enabled": true,
      "platform": "feishu_doc",
      "destination": "requester_default_space",
      "url": null
    }
  },
  "records": []
}
```

## 标准化记录

```json
{
  "record_id": "chat:oc_xxx:om_xxx",
  "source_type": "chat",
  "source_subtype": "group",
  "conversation_scope": "executive_with_enterprise_members",
  "executive_ids": ["exec_001"],
  "timestamp_start": "2026-06-09T09:12:00+08:00",
  "timestamp_end": null,
  "title": "Northstar 续约风险讨论",
  "summary": "CRO 要求法务和财务在客户会议前对齐续约折扣条款。",
  "participants": [
    {
      "name": "张伟",
      "role": "sender",
      "department": "销售部"
    }
  ],
  "business_entities": {
    "projects": ["企业续约冲刺"],
    "customers": ["Northstar"],
    "departments": ["销售部", "法务部", "财务部"],
    "metrics": ["续约 ARR"]
  },
  "activity_tags": [
    "decision",
    "risk",
    "cross_functional_coordination"
  ],
  "priority_ids": ["P1"],
  "evidence": {
    "source_url": null,
    "source_ids": ["om_xxx"],
    "quote": null
  },
  "sensitivity": "business_confidential",
  "confidence": "high"
}
```

## 来源类型

使用以下取值：

- `chat`
- `calendar`
- `task`
- `todo`
- `mail`
- `document`
- `crm`
- `manual_note`

## Conversation Scope

For chat records, use these values:

- `executive_with_boss`
- `executive_with_enterprise_members`
- `executive_group_member`
- `executive_mentioned_in_group`
- `enterprise_audit_archive`
- `unknown_or_partial`

Default expected scope is `executive_with_enterprise_members` plus relevant group scopes. If only `executive_with_boss` is available, mark the chat source as partial coverage.

## Output Targets

Use `output_targets` to separate the two report layers:

- `chat_brief`: the concise CEO-facing content returned in the chat.
- `detail_doc`: the detailed Feishu cloud document containing work details, tasks, risks, evidence IDs, and source coverage.

When `detail_doc.enabled=true`, the final chat response should include only the document URL and should not paste the full detail body.

## 敏感度取值

使用足够但不过度的最低敏感度：

- `public_business`
- `internal_business`
- `business_confidential`
- `personal_or_sensitive`
- `privileged_or_restricted`

除非请求方明确提供合法且必要的纳入理由，否则省略或重度脱敏标记为 `personal_or_sensitive` 或 `privileged_or_restricted` 的记录。

## 置信度取值

- `high`：直接来源证据支持该结论。
- `medium`：多个弱信号或部分内容支持该结论。
- `low`：由不完整来源推断，需要进一步核验。

## 证据规则

- 每个高影响决策、风险或 CEO 待办都至少需要一个证据 ID。
- 优先使用来源 ID 和简短转述，不直接输出消息原文。
- 精确引用应控制在一句话以内，并且只在原话会实质影响业务含义时使用。
