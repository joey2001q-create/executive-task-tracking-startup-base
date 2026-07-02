---
name: feishu-calendar-collector
description: Collect Feishu calendar events for an authorized user.
alwaysActive: false
---

# Feishu Calendar Collector

## Usage

```bash
feishu-calendar-collector \
  --user <open_id> \
  --start "2026-06-09T00:00:00+08:00" \
  --end "2026-06-17T23:59:59+08:00" \
  [--output file.json]
```

## Official API

- Method: `GET`
- Endpoint: `/open-apis/calendar/v4/calendars/primary/events`
- Token: `user_access_token`
- Scopes: `calendar:calendar` or `calendar:calendar.event:read`
- Query params: `start_time`, `end_time`, `page_size`

`start_time` and `end_time` are Unix timestamps in seconds. Do not use `time_min` / `time_max`.

Official response items are in `data.items`.

## Output Shape

```json
{
  "ok": true,
  "source": "calendar",
  "user": "ou_xxx",
  "count": 11,
  "items": []
}
```

## Notes

- `--start` and `--end` are required.
- The script converts ISO timestamps to Unix seconds internally.
- The script reads `user_access_token` from the external member token table.
- The token table field used to match the member is `成员`.
