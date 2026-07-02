---
name: feishu-calendar-collector
description: 飞书日程数据采集 Skill。采集指定用户在指定时间范围内的日程事件，返回标准化 JSON。
---

# 日程数据采集器

## 用法

```bash
feishu-calendar-collector collect \
  --user <open_id> \
  --start "2026-06-09T00:00:00+08:00" \
  --end "2026-06-17T23:59:59+08:00" \
  [--output file.json]
```

## 返回格式

```json
{
  "ok": true,
  "source": "calendar",
  "user": "ou_xxx",
  "count": 11,
  "items": [
    {
      "event_id": "...",
      "summary": "会议标题",
      "start_time": "2026-06-09T15:00:00+08:00",
      "end_time": "...",
      "organizer": {"name": "...", "user_id": "ou_xxx"},
      "attendees": [...],
      "location": {"name": "..."},
      "description": "..."
    }
  ]
}
```

## 依赖

- 外部用户 Token 表配置（`FEISHU_TOKEN_BASE_TOKEN` / `FEISHU_TOKEN_TABLE_ID`）
- `lark-cli`

## Token 安全传递（铁律）

**严禁直接用 shell 变量传递长 token！**

本脚本已改为 Python 实现，内部直接从多维表读取 token，避免了 shell 传递截断问题。

如需在外部调用，正确做法：
```bash
# ✅ 用Python直接读取多维表并调用API
python3 feishu-calendar-collector --user ou_xxx --start "..." --end "..."
```

## 注意事项

- 必须带 `--start` 和 `--end` 参数
- 内部自动将 ISO 时间转换为 Unix 时间戳（秒）
- 返回嵌套 JSON：`{"data":[...]}`，items 在 `data` 数组中
