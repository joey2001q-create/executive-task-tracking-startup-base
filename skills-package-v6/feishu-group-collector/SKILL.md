---
name: feishu-group-collector
description: Collect Feishu group message search results for an authorized user.
alwaysActive: false
---

# Feishu Group Collector

## Usage

```bash
feishu-group-collector \
  --user <open_id> \
  --start "2026-06-09T00:00:00+08:00" \
  --end "2026-06-17T23:59:59+08:00" \
  [--output file.json]
```

## Official API

- Method: `POST`
- Endpoint: `/open-apis/im/v1/messages/search`
- Token: `user_access_token`
- Scope: `search:message`
- Request query params: `page_size`, `page_token`, `user_id_type`
- Request body:

```json
{
  "query": "",
  "filter": {
    "time_range": {
      "start_time": "2026-06-09T00:00:00+08:00",
      "end_time": "2026-06-17T23:59:59+08:00"
    },
    "chat_type": "group"
  }
}
```

Official response items are in `data.items`.

## Output Shape

```json
{
  "ok": true,
  "source": "group",
  "user": "ou_xxx",
  "count": 19,
  "items": []
}
```

## Notes

- `--start` and `--end` are required.
- The script reads `user_access_token` from the external member token table.
- The token table field used to match the member is `成员`.
