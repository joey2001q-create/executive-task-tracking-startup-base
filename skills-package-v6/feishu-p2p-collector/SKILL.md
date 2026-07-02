---
name: feishu-p2p-collector
description: 飞书单聊（P2P）数据采集 Skill。采集指定用户与指定联系人之间的单聊消息，不遍历全组织。
---

# 单聊（P2P）数据采集器

## 用法

```bash
feishu-p2p-collector collect \
  --user <open_id> \
  --partners <partner_oid1>[,<partner_oid2>,...] \
  --start "2026-06-09T00:00:00+08:00" \
  --end "2026-06-17T23:59:59+08:00" \
  [--output file.json]
```

## 场景示例

**高管追踪**（Boss ↔ 高管）：
```bash
feishu-p2p-collector collect \
  --user ou_a033000a0351291befe54d8a05d941e5 \
  --partners {{BOSS_OPEN_ID}} \
  --start "2026-06-09T00:00:00+08:00" \
  --end "2026-06-17T23:59:59+08:00"
```

**任务追踪**（发布人 ↔ 执行人）：
```bash
feishu-p2p-collector collect \
  --user ou_xxx \
  --partners ou_yyy \
  --start "..." --end "..."
```

## 返回格式

```json
{
  "ok": true,
  "source": "p2p",
  "user": "ou_xxx",
  "count": 50,
  "items": [
    {
      "message_id": "om_xxx",
      "chat_type": "p2p",
      "chat_partner": {"open_id": "ou_xxx", "name": "..."},
      "content": "消息内容",
      "create_time": "2026-06-15 14:44",
      "sender": {"id": "ou_xxx", "name": "..."}
    }
  ]
}
```

## 实现原理

通过 `lark-cli im +chat-messages-list --user-id <partner_oid>` 直接获取指定联系人的 P2P 消息，不需要遍历全组织联系人列表。

## Token 安全传递（铁律）

**严禁直接用 shell 变量传递长 token！**

本脚本已改为 Python 实现，内部直接从多维表读取 token，避免了 shell 传递截断问题。

## 注意事项

- `--partners` 为必填参数，逗号分隔多个联系人 open_id
- 需 `im:message.p2p_msg:get_as_user` scope（需开发者后台开通）
- 敏感度高，只采集授权范围内的对话
