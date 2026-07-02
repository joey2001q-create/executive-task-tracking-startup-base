---
name: feishu-minutes-collector
description: 飞书妙记/会议纪要数据采集 Skill。采集指定用户在指定时间范围内的妙记，返回标准化 JSON。
---

# 妙记数据采集器

## 用法

```bash
feishu-minutes-collector collect \
  --user <open_id> \
  --start "2026-06-09T00:00:00+08:00" \
  --end "2026-06-17T23:59:59+08:00" \
  [--output file.json]
```

## 返回格式

```json
{
  "ok": true,
  "source": "minutes",
  "user": "ou_xxx",
  "count": 4,
  "items": [
    {
      "token": "obcnxxx",
      "topic": "会议主题",
      "owner": "所有者姓名",
      "start_time": "2026.06.16 09:58:45",
      "duration": "9 小时 5 分 52 秒",
      "app_link": "https://..."
    }
  ]
}
```

## Token 安全传递（铁律）

**严禁直接用 shell 变量传递长 token！**

本脚本已改为 Python 实现，内部直接从多维表读取 token，避免了 shell 传递截断问题。

## 注意事项

- 必须带 `--start` 和 `--end` 参数
- 返回嵌套 JSON：`{"data":{"items":[...]}}`，items 在 `data.items` 数组中
