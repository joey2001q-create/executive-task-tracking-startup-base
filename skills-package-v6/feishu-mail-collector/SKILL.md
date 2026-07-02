---
name: feishu-mail-collector
description: 飞书邮件数据采集 Skill。采集指定用户的邮件，返回标准化 JSON。
---

# 邮件数据采集器

## 用法

```bash
feishu-mail-collector collect \
  --user <open_id> \
  [--label-id INBOX] \
  [--output file.json]
```

## 返回格式

```json
{
  "ok": true,
  "source": "mail",
  "user": "ou_xxx",
  "count": 5,
  "items": [
    {
      "message_id": "...",
      "subject": "邮件主题",
      "sender": {"name": "...", "address": "..."},
      "received_time": "..."
    }
  ]
}
```

## Token 安全传递（铁律）

**严禁直接用 shell 变量传递长 token！**

本脚本已改为 Python 实现，内部直接从多维表读取 token，避免了 shell 传递截断问题。

## 注意事项

- `--label-id` 默认值为 `INBOX`，可选其他标签
- 邮件 API page_size 最大为 20
- 需 `mail:user_mailbox:readonly` 等 scope
- 飞书邮件企业版需开通才能使用
