---
name: feishu-task-collector
description: 飞书任务数据采集 Skill。采集指定用户的任务列表，返回标准化 JSON。
---

# 任务数据采集器

## 用法

```bash
feishu-task-collector collect \
  --user <open_id> \
  [--output file.json]
```

## 返回格式

```json
{
  "ok": true,
  "source": "task",
  "user": "ou_xxx",
  "count": 2,
  "items": [
    {
      "guid": "...",
      "summary": "任务标题",
      "due_at": "2026-05-28T08:00:00+08:00",
      "completed_at": null,
      "url": "https://..."
    }
  ]
}
```

## Token 安全传递（铁律）

**严禁直接用 shell 变量传递长 token！**

本脚本已改为 Python 实现，内部直接从多维表读取 token，避免了 shell 传递截断问题。

## 注意事项

- 返回全部任务，不支持时间过滤
- 如需按时间过滤，由调用方在拿到数据后自行过滤
