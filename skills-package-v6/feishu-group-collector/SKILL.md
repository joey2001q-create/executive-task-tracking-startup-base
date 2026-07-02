---
name: feishu-group-collector
description: 飞书群聊数据采集 Skill。采集指定用户在指定时间范围内的群聊消息，返回标准化 JSON。
---

# 群聊数据采集器

## 用法

```bash
feishu-group-collector collect \
  --user <open_id> \
  --start "2026-06-09T00:00:00+08:00" \
  --end "2026-06-17T23:59:59+08:00" \
  [--output file.json]
```

## 返回格式

```json
{
  "ok": true,
  "source": "group",
  "user": "ou_xxx",
  "count": 19,
  "items": [
    {
      "message_id": "om_xxx",
      "chat_id": "oc_xxx",
      "chat_name": "群名称",
      "chat_type": "group",
      "content": "消息内容",
      "create_time": "2026-06-17 11:55",
      "sender": {"id": "ou_xxx", "name": "..."}
    }
  ]
}
```

## Token 安全传递（铁律）

**严禁直接用 shell 变量传递长 token！**

本脚本已改为 Python 实现，内部直接从多维表读取 token，避免了 shell 传递截断问题。

## 注意事项

- 必须带 `--start` 和 `--end` 参数
- 内部使用消息搜索 API，自动翻页获取全部数据
- 返回嵌套 JSON：`{"data":{"messages":[...]}}`，items 在 `data.messages` 数组中
